import requests

# Define the API URL and headers
API_URL = 'http://app.sasakonnect.net:13000/api/onus/'
HEADERS = {
    'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
}

# Function to fetch data for a specific region and serial numbers
def fetch_data(region, serial_numbers):
    url = f'{API_URL}{region}'  # Construct the API URL with the provided region
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data_list = response.json()
        
        # Create a dictionary of serial numbers to their corresponding data records
        region_data = {record['Serial_Code']: record for record in data_list}
        
        # Filter region data to only include serial numbers from the serial_numbers list
        filtered_data = {serial_number: region_data.get(serial_number, {}) for serial_number in serial_numbers}
        return filtered_data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data for region {region}: {e}")
        return {}






