import requests
from datetime import datetime, timedelta
import json
import os
import pytz
import django
import sys
sys.path.append('/home/kittim/projects/konnect-app/konnect/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'konnect.settings')
django.setup()
from konnect_admin.tasks import gpon_alert


# Define the directory where building data will be stored
json_directory = '/home/kittim/projects/konnect-app/konnect/influx_data/datasets/'
# Define the API URL and headers for fetching building-to-ONU associations
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
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
    'stn': 'stnbucket',
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


# Function to fetch data for a region and organize it into a dictionary
onu_status_dict = {}
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

        return building_onus
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for region {region}: {e}")
        return {}



# Check if the request was successful
#if response.status_code == 200:
#    # Parse the JSON response
#    response_data = response.json()
#
#    print(json.dumps(response_data, indent=4))
#
#    # Extract the hits (documents) from the response
#    hits = response_data.get('hits', {}).get('hits', [])
#
#    # dictionary to associate ONU serials with their operation status
#
#
#    #onu_status_dict = {}
#
#    # Iterate through the hits and populate the dictionary
#    for hit in hits:
#        source = hit.get('_source', {})
#        serial_number = source.get('serialNumber')
#        if_oper_status = source.get('ifOperStatus')
#        elastic_timestamp = source.get('elastic_timestamp')
#
#        if serial_number and if_oper_status is not None:
#        # Map the ifOperStatus to "Online" or "Offline"
#              status = "Online" if if_oper_status == 1.0 else "Offline"
#              onu_status_dict[serial_number] = {"status": status}
#              total_records += 1
#              #print(onu_status_dict)
#    print(f'Total records collected: {total_records}')
#    # Get the list of serial numbers from the onu_status_dict
#    serial_numbers = list(onu_status_dict.keys())
#
#    # Dictionary to store building status and total ONUs
#building_status = {}
## Initialize a list to store building names that meet the criteria (5 or more ONUs)
#buildings_display = []
#
## Create a list to store building messages
#building_messages = []
#
## Initialize a dictionary to store building names and their total ONUs
#building_data_to_send = {}
#
## Find the maximum length of building names for formatting
#max_building_name_length = max(len(building) for building in building_data.keys())
#
## Iterate through buildings
#for building, onu_serials in building_data.items():
#    if len(onu_serials) >= 5:
#        # Initialize building status as "Offline"
#        building_status[building] = {"status": "Offline", "total_onus": len(onu_serials)}
#
#        # Check if any ONU in the building is online
#        for serial in onu_serials:
#            if serial in onu_status_dict and onu_status_dict[serial]["status"] == "Online":
#                building_status[building]["status"] = "Online"
#                break
#
#        if building_status[building]["status"] == "Offline":
#            # Collect building name and total ONUs
#            building_data_to_send[building] = len(onu_serials)
#
## Clear the dictionary
#onu_status_dict.clear()
#
## Prepare the message text with precise alignment
#message = f"Name{' ' * (max_building_name_length - 4)}\tONUs\n"  # Header line with adjusted space
#
#for building, total_onus in building_data_to_send.items():
#    padding = ' ' * (max_building_name_length - len(building) + 4)  # Adjust the padding here
#    message += f"{building}{padding}\t{total_onus}\n"  # Add extra space here
#
## Send the aggregated message to the alert function
#if building_data_to_send:
#    gpon_alert(message, bucket)
#



#Print the building name, status, and total ONUs
#for building, data in building_status.items():
#    print(f"Building: {building}, Status: {data['status']}, Total_ONUs: {data['total_onus']}")
#for building, data in building_status.items():
#    if data['status'] == 'Offline':
#        print(f"Building: {building}, Status: {data['status']}, Total_ONUs: {data['total_onus']}")