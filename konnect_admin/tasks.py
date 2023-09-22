from celery import shared_task
from .influx_utils import off_bldg
from .cache_bldgs import is_data_sent, cache_data
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

    # Accumulate building names in a list
    names_to_send = []

    for name in names:
        # Check if data for this building name has already been sent
        if not is_data_sent(name):
            # Add the name to the list of names to send
            names_to_send.append(name)

            # Cache the building name
            cache_data(name)

            # Add the name to the unique set for the current bucket
            unique_names_sets[bucket_name].add(name)

    # Check if there is data to send
    if names_to_send:
        # Prepare the message text with comma-separated names
        message = ", ".join(names_to_send)

        # Send the message to the Lark webhook with the dynamic title
        send_lark_alert(message, label)  # Pass 'label' as an argument

    # Print the collected 'name' values and label for verification
    print("Collected 'name' values:")
    print(unique_names_sets[bucket_name])
    print("Label:", label)


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
                    "title":label, 
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
        # Send the message to the Lark webhook
        response = requests.post(webhook_url, headers=headers, json=payload)
        response.raise_for_status()
        print("Lark alert sent successfully")
    except requests.exceptions.RequestException as e:
        print("Failed to send Lark alert:", e)
