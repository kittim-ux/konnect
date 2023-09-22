import os
import json
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from celery import Celery
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from datetime import datetime
from redcache import cache_data, get_cached_data, not_confirmed
from onu_confirmation import confirm_onu  # Import the confirm_onu function
from offline_alerts import onu_offline
from utils import extract_gpon_port, extract_olt_number
logging.basicConfig(level=logging.DEBUG)

app = Celery('onu_tasks', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

# Load environment variables
load_dotenv()
url = 'http://105.29.165.232:23027'
token = '1u1P_0nkrKLmdByZHcxZp0J7SjxRcot95qPiE82GxskxdAUCoSJiCDDvkuWmyGXQQIxyYH41y_YV0w66YeXWCA=='
org = 'techops_monitor'

# MAP buckets with their respective data
BUCKET_HOST_MAP = {
    'STNBucket': 'STN-FIBER',
    'MWKs': 'MWKs-FIBER',
    'MWKn': 'MWKn-FIBER',
    'KWDBucket': 'KWD-FIBER',
}

# Define a mapping of bucket names to Elasticsearch index names
BUCKET_INDEX_MAP = {
    'STNBucket': 'stnbucket',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDBucket': 'kwd'
}
BUCKET_REGION_MAP = {
    'STNBucket': 'stn',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDBucket': 'kwd'
    # Add more mappings as needed
}

@app.task(name='onu_status_task')
def get_onu_status(bucket):
    query = f"""from(bucket: "{bucket}")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "interface")
        |> filter(fn: (r) => r["_field"] == "ifOperStatus")
        |> filter(fn: (r) => r["host"] == "{BUCKET_HOST_MAP[bucket]}")
        |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
        |> yield(name: "mean")"""
    print(f"Fetching data from {bucket}...")

    influx_client = InfluxDBClient(url=url, token=token, org=org)
    results = influx_client.query_api().query(org=org, query=query)
    print(f"Fetched {len(results)} records from {bucket}")

    data = []
    for table in results:
        for record in table.records:
            serial_number = record.values.get("serialNumber", None)
            if serial_number:
                if_descr = record.values.get("ifDescr", "N/A")
                agent_host = record.values.get("agent_host", "N/A")
                gpon_port = extract_gpon_port(if_descr)  # Extract gpon_port from if_descr
                olt_number = extract_olt_number(agent_host)  # Extract olt_number from agent_host
                if_oper_status = record["_value"]  # Access the value of ifOperStatus

                # Check if data is cached
                cached_data = get_cached_data(bucket, serial_number)

                if not cached_data:
                    elasticsearch_timestamp = datetime.utcnow().isoformat()
                    data_entry = {
                        'bucket': bucket,
                        'ifDescr': if_descr,
                        'serialNumber': serial_number,
                        'ifOperStatus': if_oper_status,  # Include ifOperStatus in the data
                        'agent_host': agent_host,
                        'influx_timestamp': record.values['_time'].isoformat(),
                        'elastic_timestamp': elasticsearch_timestamp,
                    }
                    # Print the data before caching
                    print("Data Submitted:")
                    print(json.dumps(data_entry, indent=4))

                    if if_oper_status == 1:
                        # Data is not cached, and ifOperStatus is 1 (ONLINE), proceed to cache and confirm
                        # Cache the new data entry in Redis
                        # cache_data(bucket, serial_number, data_entry)
                        # Assuming you have the required data for confirmation (serial_number, olt_number, gpon_port)
                        confirmation_data = confirm_onu(serial_number, olt_number, gpon_port)

                        if confirmation_data:
                            # Process the confirmation data (e.g., print or save it)
                            cache_data(bucket, serial_number, data_entry)
                        else:
                            # Add the data and make it valid for 5 mins
                            not_confirmed(bucket, serial_number, data_entry)

                            print("ONU confirmation failed or encountered an error.")
                    elif if_oper_status == 2:
                        # Data is not cached, and ifOperStatus is 2 (OFFLINE), proceed to alert
                        # Determine the region_name based on the bucket parameter
                        region_name = BUCKET_REGION_MAP.get(bucket, 'unknown')
                        onu_offline(serial_number, region_name)
                        print("ONU Failed Confirmation:", offline_onu)
                else:
                    print("Data is already cached:", cached_data)

           
    # Initialize the Elasticsearch client
    es_host = os.getenv('ELASTICSEARCH_HOST')
    es_port = int(os.getenv('ELASTICSEARCH_PORT'))
    es_scheme = os.getenv('ELASTICSEARCH_SCHEME')

    es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': es_scheme}])

    # Get the Elasticsearch index name based on the bucket name
    elasticsearch_index = BUCKET_INDEX_MAP.get(bucket, None)

    if elasticsearch_index:
        # Index the data into Elasticsearch with the dynamically determined index name
        documents = []
        for entry in data:
            document = {
                'bucket': entry['bucket'],
                'ifDescr': entry['ifDescr'],
                'serialNumber': entry['serialNumber'],
                'ifOperStatus': entry['ifOperStatus'],
                'agent_host': entry['agent_host'],
                'influx_timestamp': entry['influx_timestamp'],
                'elastic_timestamp': entry['elastic_timestamp'],
            }
            json_document = json.dumps(document)
            documents.append(json_document)

        bulk(es, documents, index=elasticsearch_index)

    return 
# Celery schedule
app.conf.beat_schedule = {
    'STNBucket-STN-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 120.0,
        'args': ('STNBucket',),
    },
    'MWKs-MWKs-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 90.0,
        'args': ('MWKs',),
    },
    'MWKn-MWKn-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 80.0,
        'args': ('MWKn',),
    },
    'KWDBucket-KWD-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 60.0,
        'args': ('KWDBucket',),
    },
    # Add more schedules for other buckets
    # Add more schedules for other buckets
}

if __name__ == "__main__":
    app.start()