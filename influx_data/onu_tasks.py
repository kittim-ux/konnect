import os
import csv
import json
import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Query
from celery import Celery
import logging
import mysql.connector
logging.basicConfig(level=logging.DEBUG)


app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

load_dotenv()

token = os.getenv('token')
org = os.getenv('org')
url = os.getenv('url')

BUCKET_HOST_MAP = {
    'STNBucket': 'STN-FIBER',
    'MWKs': 'MWKs-FIBER',
}

# MySQL database configuration
mysql_host = os.getenv('mysql_host')
mysql_user = os.getenv('mysql_user')
mysql_password = os.getenv('mysql_password')
mysql_database = os.getenv('mysql_database')

# Define a dictionary to map buckets to table names
BUCKET_TABLE_MAP = {
    'STNBucket': 'sunton',
    'MWKs': 'mwikis',  # Add more mappings for other regions
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


    influx_client = InfluxDBClient(url=url, token=token, org=org)
    results = influx_client.query_api().query(org=org, query=query)

    data = []
    for table in results:
        for record in table.records:
            serial_number = record.values.get("serialNumber", None)
            if serial_number:
                data.append({
                    'ifDescr': record.values["ifDescr"],
                    'serialNumber': serial_number,
                    'ifOperStatus': record.get_value(),
                })

    # Insert data into MySQL database
    connection = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database
    )
    cursor = connection.cursor()
    # Get the corresponding table name for the region (bucket)
    table_name = BUCKET_TABLE_MAP.get(bucket, 'default_table_name')

    for entry in data:
        query = f"""
            INSERT INTO {table_name} (ifDescr, serialNumber, ifOperStatus)
            VALUES (%s, %s, %s)
        """
        values = (entry['ifDescr'], entry['serialNumber'], entry['ifOperStatus'])
        cursor.execute(query, values)

    connection.commit()
    connection.close()

    return data

# Celery schedule
app.conf.beat_schedule = {
    #'STNBucket-STN-FIBER-every-30-seconds': {
    #    'task': 'onu_status_task',
    #    'schedule': 30.0,
    #    'args': ('STNBucket',),  # Pass as a tuple
    #},
    'MWKs-MWKs-FIBER-every-30-seconds': {
        'task': 'onu_status_task',
        'schedule': 30.0,
        'args': ('MWKs','MWKs-FIBER',),  # Pass as a tuple
    },
    # Add more schedules for other buckets
}
