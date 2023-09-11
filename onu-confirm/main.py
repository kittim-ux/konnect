import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from onu_confirmation import get_new_onus, confirm_onu
from datetime import datetime, timedelta

# Specify the full path to the .env file
dotenv_path = '/home/kitim/projects/konnect-app/konnect/influx_data/.env'

# Load environment variables from the .env file
load_dotenv(dotenv_path)

# Retrieve environment variables
es_scheme = os.getenv('ELASTICSEARCH_SCHEME')
es_host = os.getenv('ELASTICSEARCH_HOST')
es_port = int(os.getenv('ELASTICSEARCH_PORT'))

es = Elasticsearch([{'scheme': 'http', 'host': es_host, 'port': es_port, }])
# Check if ELASTICSEARCH_PORT is set
if es_port is None:
    print("Error: 'ELASTICSEARCH_PORT' environment variable is not set.")
    exit(1)

try:
    es_port = int(es_port)  # Convert to an integer
except ValueError:
    print("Error: 'ELASTICSEARCH_PORT' is not a valid integer.")
    exit(1)

def main():
    # Initialize the Elasticsearch client

    # Define the Elasticsearch index name
    index_name = 'stnbucket'

    # Calculate last_check_timestamp (for example, 1 day ago)
    last_check_timestamp = datetime.now() - timedelta(days=1)

    # Get new ONUs
    new_onus = get_new_onus(es_host, index_name, last_check_timestamp)

    # Confirm each new ONU
    for onu in new_onus:
        serial_number = onu['serialNumber']
        olt_no = onu['oltNumber']
        gpon_number = onu['gponNumber']

        # Call confirm_onu to confirm the ONU on your company's site
        confirm_onu(serial_number, olt_no, gpon_number)

if __name__ == '__main__':
    main()








