import requests

# Define the API URL and headers
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
}
# Function to fetch data for a region and organize it into a dictionary
def fetch_region_data(region, serial_numbers):
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
                else:
                    # If not, create a new key with a list containing the serial code
                    building_onus[building_name] = [serial_code]

        # Print the building-serial dictionary
        print(building_onus)

        # Print the total count of buildings
        total_buildings = len(building_onus)
        print(f"Total Buildings: {total_buildings}")

        # Filter region data to only include records with serial numbers in serial_numbers list
        filtered_data = {record['Serial_Code']: record for record in data_list if record['Serial_Code'] in serial_numbers}
        return filtered_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for region {region}: {e}")
        return {}

# Usage example in onu_tasks.py to fetch region data for a specific region and serial numbers
region = 'mwkn'  # Modify the region as needed
# Assume serial_numbers is a list of serial numbers obtained from InfluxDB in onu_tasks.py
serial_numbers = ['BDCM:6DD2B9E0', 'BDCM:6DD2B9E1', 'BDCM:6DD2B9E2']  # Modify as needed

region_data = fetch_region_data(region, serial_numbers)

# Now you can use the region_data dictionary to look up building names based on serial numbers
for serial_code, record in region_data.items():
    building_name = record.get('BuildingName', 'N/A')
    print(f"Serial Code: {serial_code}, Building Name: {building_name}")

