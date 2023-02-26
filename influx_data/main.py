import json
import csv
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Query
from celery import Celery
import tasks
import logging
logging.basicConfig(level=logging.DEBUG)

app = Celery('test', broker="amqp://guest:guest@localhost:5672//",
             result_backend='rpc://')


# app.conf.update(
#     result_backend='redis://127.0.0.1:6379/0',
# )

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'mainfunc',
        'schedule': 30.0
        # 'args': (16, 16)
    },
}

load_dotenv()
# You can generate a Token from the "Tokens Tab" in the UI
token = os.getenv('token')
org = os.getenv('org')
bucket = os.getenv('bucket')
url = os.getenv('url')


# @app.task(name='hello_task')
# def main():
#     csvreadfunc()
#     return csvreadfunc

@app.task(name='mainfunc')
def csvreadfunc():
    with open("buildings.csv", "r") as f:

        reader = csv.reader(f)
        headers = next(reader)
        name = [row[0] for row in reader]
        with InfluxDBClient(url=url, token=token, org='AH', debug=False) as client:

            query_api = client.query_api()
            """
            Query: using Stream
            """
            bucketlist = ["kwtbucket"]
            for bucket in bucketlist:
                records = query_api.query_stream(f'''
                from(bucket:"{bucket}")
                |> range(start: -5m, stop: now())
                |> filter(fn: (r) => r["_measurement"] == "ping")
                |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
                |> filter(fn: (r) => r["_value"] >= 100)
                |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
                |> yield(name: "mean")''')
                if records:
                    

                    for record in records:
                        recordproc(record)
                        logging.info(record['host'])

            
def recordproc(self, record, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(record, indent=4))
            logging.info(record)