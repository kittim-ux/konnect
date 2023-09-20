from celery import shared_task
from .influx_utils import off_bldg
import json
import requests
from django.conf import settings

# Create a dictionary to store unique names sets for each bucket
unique_names_sets = {}

@shared_task
def lark_post(bucket_name):
    global unique_names_sets  # Use the global dictionary

    # Fetch data using off_bldg from influx_utils.py
    data = off_bldg(bucket_name)

    # Create a unique names set for the current bucket if it doesn't exist
    if bucket_name not in unique_names_sets:
        unique_names_sets[bucket_name] = set()

    # Extract 'name' values from the collected data
    names = [item['name'] for item in data]

    # Get the label associated with the bucket name from the mapping dictionary
    label = settings.LARK_BUCKET_LABELS.get(bucket_name, 'Unknown Bucket')

    # Add the names to the unique set for the current bucket
    unique_names_sets[bucket_name].update(names)

    # Print the collected 'name' values and label for verification
    print("Collected 'name' values:")
    print(unique_names_sets[bucket_name])
    print("Label:", label)

    # Prepare the message text
    message = f"{', '.join(unique_names_sets[bucket_name])}"  # Add two newlines for separation

    # Send the message to the Lark webhook
    send_lark_alert(message, label)  # Pass 'label' as an argument


def send_lark_alert(message, label):
    webhook_url = settings.LARK_WEBHOOK_URL  # Define this in your Django settings

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "en_us": {
                    "title": label,
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
            print("Data sent to Lark successfully!")
        else:
            print(f"Failed to send data to Lark. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while sending the data: {e}")

