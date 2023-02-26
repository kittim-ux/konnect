import json
import csv
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Query
from celery import Celery
import logging

app = Celery('test', broker="amqp://guest:guest@172.17.0.2:5672//",
             result_backend = 'rpc://')


# app.conf.update(
#     result_backend='redis://127.0.0.1:6379/0',
# )

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'hello_task',
        'schedule': 30.0,
        'args': (16, 16)
    },
}




@app.task(name='hello_task')
def hello():
    logging.info("i can be executed")