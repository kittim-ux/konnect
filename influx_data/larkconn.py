# onu_notifications.py
import json
import requests

def send_confirmation(serial_number, confirmation_data):
    if confirmation_data is None:
        # This indicates a failed confirmation, send an alert
        send_lark_alert(f"ONU Confirmation Failed for Serial Number: {serial_number}")
    else:
        # This indicates a successful confirmation, send a success message
        client_name = confirmation_data.get('ClientContact', 'N/A')
        region = confirmation_data.get('Region', 'N/A')
        building_name = confirmation_data.get('BuildingName', 'N/A')
        serial_code = confirmation_data.get('Serial_Code', 'N/A')

        confirmation_message = f"ONU Confirmation Successful:\n" \
                               f"Serial Number: {serial_number}\n" \
                               f"Client Contact: {client_name}\n" \
                               f"Region: {region}\n" \
                               f"Building Name: {building_name}\n" \
                               f"Serial Code: {serial_code}"

        send_lark_alert(confirmation_message)

    # Process the confirmation data (e.g., print or save it)
    print("ONU Confirmation Data:", confirmation_data)


def send_lark_alert(message):
    webhook_url = "https://open.larksuite.com/open-apis/bot/v2/hook/93f0c87b-bf6b-4c66-a377-26d1ce036800"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "en_us": {
                    "title": "ONU Confirmation Alert",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": message
                            }
                        ]
                    ]
                }
            }
        }
    }

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)

        if response.status_code == 200:
            print("Alert sent to Lark successfully!")
        else:
            print(f"Failed to send alert to Lark. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the alert: {e}")

