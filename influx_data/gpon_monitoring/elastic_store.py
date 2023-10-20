import os
import json
import requests
import pytz
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from .monitoring_main import REGION_JSON
from konnect_admin.tasks import gpon_alert

# Initialize the Elasticsearch client
es_host = os.getenv('ELASTICSEARCH_HOST')
es_port = int(os.getenv('ELASTICSEARCH_PORT'))
es_scheme = os.getenv('ELASTICSEARCH_SCHEME')
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': es_scheme}])

# Define the directory where building data will be stored
json_directory = '/home/kittim/projects/konnect-app/konnect/influx_data/datasets/'
# Define the API URL and headers for fetching building-to-ONU associations
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
}
# Define a mapping of bucket names to Elasticsearch index names
BUCKET_INDEX_MAP = {
    'STNOnu': 'stnbucket',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDOnu': 'kwd',
    'KSNOnu': 'ksn',
}

# Dictionary to map regions to JSON files
REGION_JSON = {
    'stn': 'stnbldg.json',
    'mwks': 'mwksbldg.json',
    'mwkn': 'mwknbldg.json',
    'kwd': 'kwdbldg.json',
    'ksn': 'ksnbldg.json',
    # Add more regions and their corresponding JSON file names here
}
#Region Bucket MAP
REGION_BUCKET_MAP = {
    'stn': 'stn',
    'mwks': 'mwks',
    'mwkn': 'mwkn',
    'kwd': 'kwd',
    'ksn': 'ksn',
    # Add more mappings as required
}

# Define your local time zone
local_timezone = pytz.timezone('Africa/Nairobi')  # Use the correct time zone

# Get the current time in your local time zone
local_now = datetime.now(local_timezone)

time_window_minutes = 5  # Adjust this value as needed
end_time = local_now
start_time = end_time - timedelta(minutes=time_window_minutes)
start_time_str = start_time.isoformat()
end_time_str = end_time.isoformat()
# Define your local time zone

# Define a flag variable to check if data has been indexed
data_indexed = False

def index_data(bucket, data, region):
    global data_indexed  # Make the flag variable global
    try:
        documents = []
        elasticsearch_index = BUCKET_INDEX_MAP.get(bucket, None)

        if elasticsearch_index:
            # Check if the index exists, and if not, create it
            if not es.indices.exists(index=elasticsearch_index):
                # Define the index settings and mappings here if needed
                # You can also use Elasticsearch index templates for more complex mappings
                es.indices.create(index=elasticsearch_index)

            for entry in data:
                # Validate data before indexing (e.g., check required fields)

                document = {
                    'region': BUCKET_INDEX_MAP.get(bucket, "N/A"),  # Dynamically set the region
                    'ifDescr': entry['ifDescr'],
                    'serialNumber': entry['serialNumber'],
                    'ifOperStatus': entry['ifOperStatus'],
                    # 'building_name': entry['building_name'],
                    'agent_host': entry['agent_host'],
                    'influx_timestamp': entry['influx_timestamp'],
                    'elastic_timestamp': entry['elastic_timestamp'],
                }
                json_document = json.dumps(document)
                documents.append(json_document)

            # Bulk indexing
            bulk(es, documents, index=elasticsearch_index)

            # Force an index refresh
            es.indices.refresh(index=elasticsearch_index)

            print(f"Data indexed into Elasticsearch for {bucket} successfully.")
            
            # Set the flag to True after data has been indexed
            data_indexed = True

            # Call the gpon_offline_data function only after data has been indexed
            if data_indexed:
                gpon_offline_data(region)
    
    except Exception as e:
        print(f"Error indexing data for {bucket} into Elasticsearch: {str(e)}")
        # Add the except block to handle exceptions
        raise e

def gpon_offline_data(region):
    url = f'http://app.sasakonnect.net:13000/api/onus/{region}'
    try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            data_list = response.json()
    
            # Create a dictionary to associate building names with Serial_Codes
            building_onus = {}
    
            for record in data_list:
                serial_code = record.get('Serial_Code')
                building_name = record.get('BuildingName')
    
                if serial_code and building_name:
                    if building_name in building_onus:
                        building_onus[building_name].append(serial_code)
                    else:
                        building_onus[building_name] = [serial_code]
    
            # Save the building_onus data to the corresponding JSON file
            json_file_path = os.path.join(json_directory, REGION_JSON.get(region))
    
            with open(json_file_path, 'w') as json_file:
                json.dump(building_onus, json_file)
    
            # Clear the building_onus dictionary
            building_onus.clear()
    
            # Load data from the JSON file
            with open(json_file_path, 'r') as json_file:
                building_data = json.load(json_file)
    
            print(f'Data for {region} has been saved to {json_file_path}')
    
            total_records = 0
            bucket = REGION_BUCKET_MAP.get(region)
            elasticsearch_url = f'http://localhost:9200/{bucket}/_search?'
    
            # Documents to be retrieved
            query = {
                "_source": ["serialNumber", "ifOperStatus", "elastic_timestamp"],
                "size": 2500,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "elastic_timestamp": {
                                        "gte": start_time_str,
                                        "lte": end_time_str
                                    }
                                }
                            }
                        ]
                    }
                }
            }# Send the search request to Elasticsearch
            response = requests.post(elasticsearch_url, json=query)
    
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                response_data = response.json()
            
                print(json.dumps(response_data, indent=4))
            
                # Extract the hits (documents) from the response
                hits = response_data.get('hits', {}).get('hits', [])
            
                # dictionary to associate ONU serials with their operation status
                onu_status_dict = {}
            
                # Iterate through the hits and populate the dictionary
                for hit in hits:
                    source = hit.get('_source', {})
                    serial_number = source.get('serialNumber')
                    if_oper_status = source.get('ifOperStatus')
                    elastic_timestamp = source.get('elastic_timestamp')
            
                    if serial_number and if_oper_status is not None:
                    # Map the ifOperStatus to "Online" or "Offline"
                          status = "Online" if if_oper_status == 1.0 else "Offline"
                          onu_status_dict[serial_number] = {"status": status}
                          total_records += 1
                #print(onu_status_dict)
                print(f'Total records collected: {total_records}')
#               # Get the list of serial numbers from the onu_status_dict
                serial_numbers = list(onu_status_dict.keys())
                
                # Dictionary to store building status and total ONUs
            building_status = {}
            # Initialize a list to store building names that meet the criteria (5 or more ONUs)
            buildings_display = []
            
            # Create a list to store building messages
            building_messages = []
            
            # Initialize a dictionary to store building names and their total ONUs
            building_data_to_send = {}
            
            # Find the maximum length of building names for formatting
            max_building_name_length = max(len(building) for building in building_data.keys())
            
            for building, onu_serials in building_data.items():
                if len(onu_serials) >= 5:
                    # Initialize building status as "Offline"
                    building_status[building] = {"status": "Offline", "total_onus": len(onu_serials)}
            
                    # Check if any ONU in the building is online
                    for serial in onu_serials:
                        if serial in onu_status_dict and onu_status_dict[serial]["status"] == "Online":
                            building_status[building]["status"] = "Online"
                            break
            
                    if building_status[building]["status"] == "Offline":
                        # Collect building name and total ONUs
                        building_data_to_send[building] = len(onu_serials)
            
            # Clear the dictionary
            onu_status_dict.clear()
            
            # Prepare the message text with precise alignment
            message = f"Name{' ' * (max_building_name_length - 4)}\tONUs\n"  # Header line with adjusted space
            
            for building, total_onus in building_data_to_send.items():
                padding = ' ' * (max_building_name_length - len(building) + 4)  # Adjust the padding here
                message += f"{building}{padding}\t{total_onus}\n"  # Add extra space here
            
            # Send the aggregated message to the alert function
            if building_data_to_send:
                gpon_alert(message, region)
                print(message)
            
            #            
    except requests.exceptions.RequestException as e:
     print(f"An error occurred while fetching data for region {region}: {e}")
     # Add the except block to handle exceptions
   
    






                            

