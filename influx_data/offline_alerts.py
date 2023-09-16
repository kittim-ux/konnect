import requests

def onu_offline(serial_number, region_name):
    url = f"http://app.sasakonnect.net:13000/api/onus/{region_name}"
    params = {
        "serial_code": [serial_number],  # Use "serial_code" as the parameter name
    }
    # Define the headers with the bearer token
    headers = {
        'Authorization': 'Bearer SX10u7hcvNVDUAGkIkV0SoCspfJGk6DXdFqNmwLHS2zsOGA1ruJ4t3fPMgZsT2mCeW5nMSeSK06KGPMH',
    }

    try:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data_list = response.json()

            if data_list:
                # Retrieve client details from the first item in the list
                first_item = data_list[0]
                client_name = first_item.get("ClientContact", "N/A")
                region = first_item.get("Region", "N/A")
                building_name = first_item.get("BuildingName", "N/A")
                serial_code = first_item.get("Serial_Code", "N/A")

                return {
                    "ClientContact": client_name,
                    "Region": region,
                    "BuildingName": building_name,
                    "Serial_Code": serial_code,
                }
            else:
                print("No data found in the response.")
                return None
        else:
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None