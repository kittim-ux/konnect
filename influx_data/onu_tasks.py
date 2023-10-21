import os
import json
import csv
import pytz
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from celery import Celery
import logging
from datetime import datetime, timedelta
from redcache import cache_data, get_cached_data
from onu_confirmation import confirm_onu  # Import the confirm_onu function
from gpon_monitoring.offline_alerts import onu_offline
from utils import extract_gpon_port, extract_olt_number
from gpon_monitoring.elastic_store import index_data
#from gpon_monitoring.monitoring_main import gpon_offline_data, onu_status_dict
logging.basicConfig(level=logging.DEBUG)

# Define your local time zone
local_timezone = pytz.timezone('Africa/Nairobi')  # Use the correct time zone

# Get the current time in your local time zone
local_now = datetime.now(local_timezone)

app = Celery('onu_tasks', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

# Load environment variables
load_dotenv()
url = 'http://105.29.165.232:23027'
token = '1u1P_0nkrKLmdByZHcxZp0J7SjxRcot95qPiE82GxskxdAUCoSJiCDDvkuWmyGXQQIxyYH41y_YV0w66YeXWCA=='
org = 'techops_monitor'

# MAP buckets with their respective data
BUCKET_HOST_MAP = {
    'STNOnu': 'STN-FIBER',
    'MWKs': 'MWKs-FIBER',
    'MWKn': 'MWKn-FIBER',
    'KWDOnu': 'KWD-FIBER',
    'KSNOnu': 'KSN-FIBER',
}

# Define a mapping of bucket names to Elasticsearch index names
BUCKET_INDEX_MAP = {
    'STNOnu': 'stnbucket',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDOnu': 'kwd',
    'KSNOnu': 'ksn',
}
BUCKET_REGION_MAP = {
    'STNOnu': 'stn',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDOnu': 'kwd',
    'KSNOnu': 'ksn',
    # Add more mappings as needed
}

#data_indexed = False
@app.task(name='onu_status_task')
def get_onu_status(bucket):
    #global data_indexed  # Use the global flag
    query = f"""from(bucket: "{bucket}")
        |> range(start: -1m)
        |> filter(fn: (r) => r["_measurement"] == "interface")
        |> filter(fn: (r) => r["_field"] == "ifOperStatus")
        |> filter(fn: (r) => r["host"] == "{BUCKET_HOST_MAP[bucket]}")
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        |> yield(name: "mean")"""
    #print(f"Fetching data from {bucket}...")

    influx_client = InfluxDBClient(url=url, token=token, org=org)
    results = influx_client.query_api().query(org=org, query=query)
    #print(f"Fetched {len(results)} records from {bucket}")

    data = []
    # Open the CSV file in write mode and create a CSV writer
    csv_file_path = 'offline_onu.csv'
    with open(csv_file_path, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        serial_numbers = []
        for table in results:
            for record in table.records:
                serial_number = record.values.get("serialNumber", None)
                if serial_number and record["_value"] == 2:  # Check if ifOperStatus is 2 (OFFLINE)
                    # Write the serial number to the CSV file
                    csv_writer.writerow([serial_number])

                if serial_number:
                    serial_number = serial_number.replace("Ahdi:", "BDCM:")
                    if_descr = record.values.get("ifDescr", "N/A")
                    agent_host = record.values.get("agent_host", "N/A")
                    gpon_port = extract_gpon_port(if_descr)  # Extract gpon_port from if_descr
                    olt_number = extract_olt_number(agent_host)  # Extract olt_number from agent_host
                    if_oper_status = record["_value"]  # Access the value of ifOperStatus
                    serial_numbers.append(serial_number)

        # After collecting all serial numbers, you can fetch region data
        region = BUCKET_REGION_MAP.get(bucket, "N/A")
        #region_data = fetch_data.fetch_data(region, serial_numbers)  # Use fetch_data function

        for serial_number in serial_numbers:
            # Update elastic_timestamp for each record
            elastic_timestamp = datetime.now(local_timezone).isoformat(),
            # Create the data entry dictionary for this record
            data_entry = {
                'region': region,
                'ifDescr': if_descr,
                'serialNumber': serial_number,
                'ifOperStatus': if_oper_status,
                'agent_host': agent_host,
                'influx_timestamp': record.values['_time'].isoformat(),
                'elastic_timestamp': elastic_timestamp,
            }
            # Append the data entry to the list of all data entries
            data.append(data_entry)
            # Check if data is cached
            cached_data = get_cached_data(bucket, serial_number)

            if not cached_data:
                # Print the data before caching
                #print("Data Missing in the Cache")
                #print(json.dumps(data_entry, indent=4))

                if if_oper_status == 1:
                    # Data is not cached, and ifOperStatus is 1 (ONLINE), proceed to cache and confirm
                    # Cache the new data entry in Redis
                    # cache_data(bucket, serial_number, data_entry)
                    # Assuming you have the required data for confirmation (serial_number, olt_number, gpon_port)
                    confirmation_data = confirm_onu(serial_number, olt_number, gpon_port)
                    if confirmation_data:
                        # Process the confirmation data (e.g., print or save it)
                        cache_data(bucket, serial_number, data_entry)
                        #print(json.dumps({
                        #    'bucket': bucket,
                        #    'ifDescr': if_descr,
                        #    'serialNumber': serial_number,
                        #    'ifOperStatus': if_oper_status,
                        #    'agent_host': agent_host,
                        #    'gpon_port': gpon_port,
                        #    'olt_number': olt_number
                        #}, indent=4))
                    else:
                        # Handle failed confirmation
                        #not_confirmed(bucket, serial_number, data_entry)
                        #print("ONU confirmation failed or encountered an error.")
                        csv_writer.writerow([serial_number])
                        #print(serial_number)
    # Index the data into Elasticsearch
    region = BUCKET_INDEX_MAP.get(bucket, "N/A")
    index_data(bucket, data, region)
    #total_data = len(data)
    #print(f"Total Records indexed: {total_data}")
            

    return  
# Ce#lery schedule
app.conf.beat_schedule = {
    'STNOnu-STN-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 700.0,
        'args': ('STNOnu',),
    },
    'MWKs-MWKs-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 60.0,
        'args': ('MWKs',),
    },
    'MWKn-MWKn-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 80.0,
        'args': ('MWKn',),
    },
    'KWDOnu-KWD-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 100.0,
        'args': ('KWDOnu',),
    },
    'KSNOnu-KSN-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 110.0,
        'args': ('KSNOnu',),
    },
     #Add more schedules for other buckets
    # Add more schedules for other buckets
}

if __name__ == "__main__":
    app.start()