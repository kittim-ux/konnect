import os
import csv
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/home/kitim/projects/konnect-app/konnect/influx_data/.env')
load_dotenv(dotenv_path=dotenv_path)

# importing the payment auth
pay_api = os.getenv('pay_api')
pay_auth = os.getenv('pay_auth')

class Payments:
    def __init__(self):
        self.pay_api = pay_api
        self.pay_auth = pay_auth
    def get_payments(self):
        payment_client = requests.get(self.pay_api, self.pay_auth)
        if payment_client.status_code == 200:
            data = payment_client.json()
            user = data["user"]
            phone = data["phone"]
            time = data["time"]
            print(user, phone, time)
        else:
            print("Failed to retrieve data from the API endpoint. Status code:", payment_client.status_code)
obj = Payments()
obj.get_payments()