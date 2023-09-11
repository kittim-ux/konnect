from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import os


dotenv_path = '/home/kitim/projects/konnect-app/konnect/influx_data/.env'

# Load environment variables from the .env file
load_dotenv(dotenv_path)

# Retrieve environment variables
es_scheme = os.getenv('ELASTICSEARCH_SCHEME')
es_host = os.getenv('ELASTICSEARCH_HOST')
es_port = int(os.getenv('ELASTICSEARCH_PORT'))

def get_new_onus(es_host, index_name, last_check_timestamp):
    # Initialize the Elasticsearch client
    es = Elasticsearch([{'scheme': 'http', 'host': es_host, 'port': es_port, }])

    # Define the Elasticsearch query to filter new ONUs
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "elastic_timestamp": {
                                "gt": last_check_timestamp
                            }
                        }
                    }
                ]
            }
        }
    }

    # Use Elasticsearch's scan API to efficiently retrieve matching documents
    scanner = scan(es, query=query, index=index_name)

    new_onus = []

    for result in scanner:
        source = result['_source']
        new_onus.append(source)

    return new_onus

# Example usage
if __name__ == "__main__":
    elasticsearch_host = "http://localhost:9200"  # Replace with your Elasticsearch host
    index_name = "stnbucket"  # Replace with your index name
    last_check_timestamp = datetime.now() - timedelta(days=1)  # Replace with your last check timestamp

    new_onus = check_for_new_onus(elasticsearch_host, index_name, last_check_timestamp)

    if new_onus:
        print("New ONUs found:")
        for onu in new_onus:
            print(onu)
    else:
        print("No new ONUs found.")

def confirm_onu(serial_number, olt_no, gpon_number):
    # Define the API endpoint and request payload
    api_url = "http://app.sasakonnect.net:13000/api/onu-confirmation"
    
    # Define the request payload as a dictionary
    payload = {
        "serial_number": serial_number,
        "olt_no": olt_no,
        "gpon_number": gpon_number
    }

    try:
        # Send a POST request to the API endpoint with the payload
        response = requests.post(api_url, json=payload)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            print(f"ONU confirmed successfully: Serial Number {serial_number}")
            return True
        else:
            print(f"Failed to confirm ONU: Serial Number {serial_number}")
            print(f"HTTP Status Code: {response.status_code}")
            return False

    except Exception as e:
        print(f"An error occurred while confirming ONU: Serial Number {serial_number}")
        print(f"Error: {str(e)}")
        return False

# Example usage:
if __name__ == "__main__":
    serial_number = "BDCM:8E04B1F0"  # Replace with the serial number of the ONU
    olt_no = "GPON0"  # Replace with the OLT number
    gpon_number = "6:14"  # Replace with the GPON port number

    confirmation_result = confirm_onu(serial_number, olt_no, gpon_number)

    if confirmation_result:
        print("ONU confirmation successful.")
    else:
        print("ONU confirmation failed.")
