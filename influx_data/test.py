import os
import csv
import json
<<<<<<< HEAD
=======
import requests
>>>>>>> e2a106d (added db folder)
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
<<<<<<< HEAD

app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

dataset_dir = '/home/kittim/Documents/projects/admindash/konnect/influx_data/datasets'
=======
#webhook_url = os.getenv('webhook_url')

webhook_url = "https://open.larksuite.com/open-apis/bot/v2/hook/5b08e3be-a43e-4186-882f-acca7712f280"
app = Celery('test', broker="amqp://guest:guest@localhost:5672//", result_backend='rpc://')

dataset_dir = '/home/kitim/projects/konnect-app/konnect/influx_data/datasets'
>>>>>>> e2a106d (added db folder)
bucket_map = {
        'kwtbldg': 'kwtbucket',
        'g44bldg': 'g44bucket',
        'zmmbldg': 'zmmbucket',
        'rmmbldg': 'RMM',
        'g45nbldg': 'G45NBucket'
}
<<<<<<< HEAD

@app.task(name='all_buildings')
def all_buildings(bucket, host):
=======
def send_to_webhook(webhook_url, data):
    headers = {'Content-type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, json=data)
    response.raise_for_status()

@app.task(name='all_buildings')
def all_buildings(bucket, host, webhook_url):
>>>>>>> e2a106d (added db folder)
    influx_client = InfluxDBClient(url=url, token=token, org=org)
    with open(os.path.join(dataset_dir, f"{bucket}.csv"), "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        names = [row[0] for row in reader]
    

    all_results = []
    for name in names:
        query_string = f"""from(bucket: "{bucket_map[bucket]}")
            |> range(start: -1m)
            |> filter(fn: (r) => r["_measurement"] == "ping")
            |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
            |> filter(fn: (r) => r["host"] == "{host}")
            |> filter(fn: (r) => r["name"] == "{name}")
            |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
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

<<<<<<< HEAD
=======
    send_to_webhook(webhook_url, all_results)
    print(webhook_url)

>>>>>>> e2a106d (added db folder)
    return all_results

app.conf.beat_schedule = {
    'kwtbucket-kwt-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
<<<<<<< HEAD
        'args': ('kwtbldg', 'KWT-FIBER'),
=======
        'args': ('kwtbldg', 'KWT-FIBER', webhook_url),
        
>>>>>>> e2a106d (added db folder)
    },
    'g44bucket-g44-fiber-every-30-seconds': {
        'task': 'all_buildings',
       'schedule': 30.0,
<<<<<<< HEAD
        'args': ('g44bldg', 'G44-FIBER'),
=======
        'args': ('g44bldg', 'G44-FIBER', webhook_url),
>>>>>>> e2a106d (added db folder)
    },
   'zmmbucket-zmm-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
<<<<<<< HEAD
        'args': ('zmmbldg', 'ZMM-FIBER'),
=======
        'args': ('zmmbldg', 'ZMM-FIBER', webhook_url),
>>>>>>> e2a106d (added db folder)
    },
    'rmm-roy-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
<<<<<<< HEAD
        'args': ('rmmbldg', 'ROY-FIBER'),
=======
        'args': ('rmmbldg', 'ROY-FIBER', webhook_url),
>>>>>>> e2a106d (added db folder)
    },
    'g45n-fiber-every-30-seconds': {
        'task': 'all_buildings',
        'schedule': 30.0,
<<<<<<< HEAD
        'args': ('g45nbldg', 'G45N-FIBER'),
=======
        'args': ('g45nbldg', 'G45N-FIBER', webhook_url),
>>>>>>> e2a106d (added db folder)
    },
}



##app = Celery('test', broker="amqp://guest:guest@172.17.0.2:5672//",
#             result_backend = 'rpc://')
#
#
## app.conf.update(
##     result_backend='redis://127.0.0.1:6379/0',
## )
#
#app.conf.beat_schedule = {
#    'add-every-30-seconds': {
#        'task': 'tasks.fetch_influx',
#        'schedule': 30.0,
#        'args': (16, 16)
#    },
#}
#
#load_dotenv()
## You can generate a Token from the "Tokens Tab" in the UI
#token = os.getenv('token')
#org = os.getenv('org')
#bucket = os.getenv('bucket')
#
#
#class InfluxClient:
#
#    def __init__(self, token, org=org, bucket=bucket):
#        self._org = org
#        self._bucket = bucket
#        self._client = InfluxDBClient(
#            url="http://app.sasakonnect.net:8086", token=token, org=org)
#
#    def query_data(self, query):
#        query_api = self._client.query_api()
#        result = query_api.query(org=self._org, query=query)
#        results = []
#        for table in result:
#            for record in table.records:
#                results.append({
#                    'name': record.values["name"],
#                    'value': record.get_value(),
#                    'field': record.get_field(),
#                    'measurement': record.get_measurement()
#                })
#        return results
#
#    def write_to_file(self, data, filename):
#        with open(filename, "w") as file:
#            file.write(json.dumps(data, indent=4))
#
#
#dataset_dir = '/home/kittim/Documents/projects/admindash/konnect/influx_data/datasets'
#
#
#@app.task(name='fetch_influx')
#def run_influx_query():
#    for dataset in os.walk(dataset_dir):
#        helper(dataset)
#        # print(dataset)
#        # with open("buildings.csv", "r") as f:
#        #     reader = csv.reader(f)
#        #     headers = next(reader)
        #     name = [row[0] for row in reader]
        # influx_client = InfluxClient(token, org, bucket)
        # bucket_list = ["g45bucket"]
        # all_results = []
        # for name in name:
        #     query_string = f"""from(bucket: "{bucket_list}")
        #         |> range(start: -1m)
        #         |> filter(fn: (r) => r["_measurement"] == "ping")
        #         |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
        #         |> filter(fn: (r) => r["host"] == "KWT-FIBER")
        #         |> filter(fn: (r) => r["name"] == "{name}")
        #         |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
        #         |> yield(name: "mean")"""
        #     data = influx_client.query_data(query_string)
        #     all_results += data

        #     influx_client.write_to_file(all_results, "data.json")


#def helper():
#    with open("buildings.csv", "r") as f:
#            reader = csv.reader(f)
#            headers = next(reader)
#            name = [row[0] for row in reader]
#            print(headers)
#    f.close()
            
        

# if __name__ == "__main__":
#     app.start()

# # Submit a task to the Celery worker
#     run_influx_query.apply_async()
#     app.add_periodic_task(120.0, run_influx_query.s(), name='Run Influx Query every 2 minutes')

# print(f"Data Successfully written to data.json")



       
    
