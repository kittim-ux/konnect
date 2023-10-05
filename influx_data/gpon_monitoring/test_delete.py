import requests
import json
#from datetime import datetime, timedelta

# Define the API URL and headers for fetching building-to-ONU associations
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
}

# Function to fetch data for a region and organize it into a dictionary
def fetch_region_data(region):
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
                # Check if the building name is already a key in the dictionary
                if building_name in building_onus:
                    building_onus[building_name].append(serial_code)
                    print(building_onus)
                else:
                    # If not, create a new key with a list containing the serial code
                    building_onus[building_name] = [serial_code]

        return building_onus
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for region {region}: {e}")
        return {}

# Define the Elasticsearch search endpoint URL
elasticsearch_url = 'http://localhost:9200/stnbucket/_search'

# Documents to be retrieved
query = {
    "_source": ["serialNumber", "ifOperStatus", "building_name"],
    "size": 2000,
    "query": {
        "match_all": {}  # Match all documents
    }
}

# Send the search request to Elasticsearch
response = requests.post(elasticsearch_url, json=query)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    response_data = response.json()

    #print(json.dumps(response_data, indent=4))

    # Extract the hits (documents) from the response
    hits = response_data.get('hits', {}).get('hits', [])

    # dictionary to associate ONU serials with their operation status
    onu_status_dict = {}

    # Iterate through the hits and populate the dictionary
    for hit in hits:
        source = hit.get('_source', {})
        serial_number = source.get('serialNumber')
        if_oper_status = source.get('ifOperStatus')
        building_name = source.get('building_name')

        if serial_number and if_oper_status is not None:
        # Map the ifOperStatus to "Online" or "Offline"
              status = "Online" if if_oper_status == 1.0 else "Offline"
              onu_status_dict[serial_number] = {"status": status, "building_name": building_name}

    # Now you can use the onu_status_dict and the building_onus dictionary
    target_region = 'stn'  # Modify the region as needed
    building_onus = fetch_region_data(target_region)

    # Get the list of serial numbers from the onu_status_dict
    serial_numbers = list(onu_status_dict.keys())

    # Dictionary to store building status and total ONUs
building_status = {}

# Iterate through buildings
for building, onu_serials in building_onus.items():
    # Initialize building status as "Offline"
    building_status[building] = {"status": "Offline", "total_onus": len(onu_serials)}

    # Check if any ONU in the building is online
    for serial in onu_serials:
        if serial in onu_status_dict and onu_status_dict[serial]["status"] == "Online":
            building_status[building]["status"] = "Online"
            break

# Print the building name, status, and total ONUs
for building, data in building_status.items():
    print(f"Building: {building}, Status: {data['status']}, Total_ONUs: {data['total_onus']}")



