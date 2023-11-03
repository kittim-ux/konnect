import os
import json
import requests
from konnect_admin.tasks import gpon_alert


# Define the directory where building data will be stored
json_directory = '/home/kittim/projects/konnect-app/konnect/influx_data/datasets/'

# Dictionary to map regions to JSON files
REGION_JSON = {
    'stn': 'stnbldg.json',
    'mwks': 'mwksbldg.json',
    'mwkn': 'mwknbldg.json',
    'kwd': 'kwdbldg.json',
    'ksn': 'ksnbldg.json',
    # Add more regions and their corresponding JSON file names here
}

data_indexed = False

def data_to_json(bucket, data_to_index, region):
    print(region)
    try:
        json_directory = '/home/kittim/projects/konnect-app/konnect/influx_data/datasets/onus_status/'  # Specify the directory where JSON files will be stored

        # Define a filename based on region and bucket
        filename = f"{region}.json"

        # Create a set to store unique serial numbers
        unique_serial_numbers = set()

        # Filter out duplicate entries and replace "Ahdi" with "AHDI" in serial numbers
        filtered_data = []
        for entry in data_to_index:
            if 'serialNumber' in entry:
                serial_number = entry['serialNumber']
                serial_number = serial_number.upper().replace("Ahdi", "AHDI")  # Replace "Ahdi" with "AHDI"
                if not any(serial_number.startswith(prefix) for prefix in unique_serial_numbers):
                    unique_serial_numbers.add(serial_number)
                    entry['serialNumber'] = serial_number
                    filtered_data.append(entry)



        
        with open(os.path.join(json_directory, filename), 'w') as json_file:
            json.dump(filtered_data, json_file, indent=4)

        # Log that data has been indexed to JSON files
        print(f"Data indexed to JSON file for {bucket} in {region}.")

        # Set the flag to True after data has been indexed
        global data_indexed
        data_indexed = True
        if data_indexed:
            bldg_onus_data(region)

    except Exception as e:
        print(f"Error indexing data to JSON file for {bucket}: {str(e)}")
        # Add the except block to handle exceptions
        raise e
#############################################################################################################
def bldg_onus_data(region):
    json_file_path = os.path.join(json_directory, REGION_JSON.get(region, ''))

    if not json_file_path or not os.path.isfile(json_file_path):
        return None  # Return None if the file doesn't exist

    try:
        with open(json_file_path, 'r') as json_file:
            building_data = json.load(json_file)
            #print(building_data)
        offline_process(building_data, region)
        return building_data
    except Exception as e:
        #print(f"Error reading data from JSON file for {region}: {str(e)}")
        return None  # Return None in case of an error

############################################################################################################
def offline_process(building_data, region):
    json_directory = '/home/kittim/projects/konnect-app/konnect/influx_data/datasets/onus_status/'
    try:
        # Define a filename based on region
        filename = f"{region}.json"
        json_file_path = os.path.join(json_directory, filename)

        with open(json_file_path, 'r') as json_file:
            data_to_process = json.load(json_file)

        # Process the data (modify this part as per your requirements)
        total_records = 0
        onu_status_dict = {}

        for entry in data_to_process:
            serial_number = entry.get('serialNumber', 'N/A')
            if_oper_status = entry.get('ifOperStatus', 'N/A')
            if serial_number and if_oper_status is not None:
                # Map the ifOperStatus to "Online" or "Offline"
                status = "Online" if if_oper_status == 1.0 else "Offline"
                onu_status_dict[serial_number] = {"status": status}
                total_records += 1
                #print(onu_status_dict)

        print(f'Total records collected: {total_records}')

        # Initialize building data to send
        building_data_to_send = {}
        
        # Find the maximum length of building names for formatting
        max_building_name_length = max(len(building) for building in building_data.keys())
        
        for building, onu_serials in building_data.items():
            # Only process buildings with more than 5 ONUs
            if len(onu_serials) > 5:
                # Initialize building status as "Offline"
                building_status = {"building": building, "status": "Offline", "total_onus": len(onu_serials)}
                # Check if any ONUs in the building are online
                for serial in onu_serials:
                    if serial in onu_status_dict and onu_status_dict[serial]["status"] == "Online":
                        building_status["status"] = "Online"
                        break  # No need to check further if one "Online" ONU is found
                # Collect building name and total ONUs
                building_data_to_send[building] = building_status
        
        # Prepare the message text with precise alignment for offline buildings
        message = f"Name{' ' * (max_building_name_length - 4)}\tONUs\n"  # Header line with adjusted space
        
        for building, status in building_data_to_send.items():
            # If the building is Offline, don't include the "Offline" status in the message
            if status['status'] == "Offline":
                padding = ' ' * (max_building_name_length - len(building) + 4)  # Adjust the padding here
                message += f"{building}{padding}\t{status['total_onus']}\n"  # Add extra space here
        
        # Send the aggregated message to the alert function
        if any(status['status'] == "Offline" for status in building_data_to_send.values()):
            #gpon_alert(message, region)
            print(message)


    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for region {region}: {str(e)}")
    # Add the except block to handle exceptions