import os
import csv
import json
import requests
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Query
from celery import Celery
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# You can generate a Token from the "Tokens Tab" in the UI
token = os.getenv('token')
org = os.getenv('org')
url = os.getenv('url')


app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

dataset_dir = '/home/kittim/Documents/projects/admindash/konnect/influx_data/datasets'
#webhook_url = os.getenv('webhook_url')

webhook_url = "https://open.larksuite.com/open-apis/bot/v2/hook/5b08e3be-a43e-4186-882f-acca7712f280"
app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

dataset_dir = '/home/kitim/projects/konnect-app/konnect/influx_data/datasets'
bucket_map = {
        'kwtbldg': 'kwtbucket',
        'g44bldg': 'g44bucket',
        'zmmbldg': 'zmmbucket',
        'rmmbldg': 'RMM',
        'g45nbldg': 'G45N1Bucket'
}

@app.task(name='all_buildings')
def all_buildings(bucket, host, webhook_url):
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    with open(os.path.join(dataset_dir, f"{bucket}.csv"), "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        names = []

        for row in reader:
            try:
                name = row[0]
                names.append(name)
            except IndexError:
                # Handle the case where the row doesn't have enough elements
                pass

    all_results = []
    for name in names:
        query_string = f"""from(bucket: "{bucket_map[bucket]}")
            |> range(start: -10m)
            |> filter(fn: (r) => r["_measurement"] == "ping")
            |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
            |> filter(fn: (r) => r["host"] == "{host}")
            |> filter(fn: (r) => r["name"] == "{name}")
            |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
            |> yield(name: "mean")"""
        results = influx_client.query_api().query(query_string)
        data = []
        for table in results:
            for record in table.records:
                if record.get_value() == 100:
                    data.append({
                        'name': record.values["name"],
                        'value': record.get_value(),
                        'field': record.get_field(),
                        'measurement': record.get_measurement()
                    })
        all_results += data

    with open("data.json", "w") as file:
        file.write(json.dumps(all_results, indent=4))

    return all_results
app.conf.beat_schedule = {
    'kwtbucket-kwt-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
        'args': ('kwtbldg', 'KWT-FIBER'),

        'args': ('kwtbldg', 'KWT-FIBER', webhook_url),
        
    },
    'g44bucket-g44-fiber-every-30-seconds': {
        'task': 'all_buildings',
       'schedule': 30.0,

        'args': ('g44bldg', 'G44-FIBER'),
        'args': ('g44bldg', 'G44-FIBER', webhook_url),
    },
     'zmmbucket-zmm-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
        'args': ('zmmbldg', 'ZMM-FIBER', webhook_url),
#
    },
    'rmm-roy-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
        'args': ('rmmbldg', 'ROY-FIBER'),
        'args': ('rmmbldg', 'ROY-FIBER', webhook_url),
    },
    'g45n-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
        'args': ('g45nbldg', 'G45N-FIBER'),
        'args': ('g45nbldg', 'G45N-FIBER', webhook_url),

    },
}
