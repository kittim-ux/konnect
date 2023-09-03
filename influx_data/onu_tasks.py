import os
import csv
import json
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from celery import Celery
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logging.basicConfig(level=logging.DEBUG)

app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

# Load environment variables
load_dotenv()
token = os.getenv('token')
org = os.getenv('org')
url = os.getenv('url')
#MAP buckets with their respective data
BUCKET_HOST_MAP = {
    'STNBucket': 'STN-FIBER',
    'MWKs': 'MWKs-FIBER',
}

# Define a mapping of bucket names to Elasticsearch index names
BUCKET_INDEX_MAP = {
    'STNBucket': 'stnbucket',
    'MWKs': 'mwks',
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
                data.append({
                    'ifDescr': record.values["ifDescr"],
                    'serialNumber': serial_number,
                    'ifOperStatus': record.get_value(),
                    #'timestamp': record.get_field(),
                })

 
    
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
                'ifDescr': entry['ifDescr'],
                'serialNumber': entry['serialNumber'],
                'ifOperStatus': entry['ifOperStatus'],
                #'timestamp': entry['timestamp'],
            }
            json_document = json.dumps(document)  # Convert the document to a JSON string
            documents.append(json_document)
    
        # Use the Elasticsearch bulk API to write the documents to Elasticsearch in batches
        bulk(es, documents, index=elasticsearch_index)

    
    return data


# Celery schedule
app.conf.beat_schedule = {
    'STNBucket-STN-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 60.0,
        'args': ('STNBucket',),
    },
    'MWKs-MWKs-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 60.0,
        'args': ('MWKs',),
    },
    # Add more schedules for other buckets
}
