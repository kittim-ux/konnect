import requests
import json

def confirm_onu(serial_number, olt_number, gpon_port):
    # Define the API URL
    api_url = "http://app.sasakonnect.net:13000/api/onu-confirmation"

    # Define the data to be sent in the POST request
    data = {
        'serial_code': serial_number,
        'olt': olt_number,
        'gpon': gpon_port
    }

    # Define the headers with the bearer token
    headers = {
        'Authorization': 'Bearer DORFvnijCPZBUNm9KWgmaKncQthhm5QRcq2n356Qz56BP79G9wOPbsm83cyTOZ852CjCjxDUfSQzJEvz',
    }

    try:
        # Send an HTTP POST request to the API with JSON data and headers
        response = requests.post(api_url, json=data, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the API response, which may contain confirmation details
            confirmation_data = response.json()
            return confirmation_data
        else:
            # Handle API request errors here (e.g., raise an exception or log)
            #print("API request failed with status code:", response.status_code)
            return None
    except Exception as e:
        # Handle exceptions (e.g., network errors) here
        #print("An error occurred while making the API request:", str(e))
        return None



