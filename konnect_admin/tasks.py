import logging
from celery import shared_task
from .influx_utils import off_bldg, pop_monitor
from .cache_bldgs import is_data_sent, cache_data, pop_cache_data
import json
import requests
from django.conf import settings

# Configure the logger
logger = logging.getLogger(__name__)

def send_lark_alert(message, label, webhook_url):
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
        # Send the message to the specified Lark webhook URL
        response = requests.post(webhook_url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Lark alert sent successfully")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send Lark alert: %s", e)

@shared_task
# PoP monitoring############################################
def lark_post_pop(bucket_name):
    global unique_names_sets  # Define the global dictionary

    # Initialize unique_names_sets as an empty dictionary if it doesn't exist
    if 'unique_names_sets' not in globals():
        unique_names_sets = {}

    # Check if the bucket_name is in the POP_BUCKET_MAPPING
    if bucket_name in settings.POP_BUCKET_MAPPING:
        # Fetch data using a function specific to PoP power outages
        data = pop_monitor(bucket_name)
        print(data)
        logger.debug("Data fetched for bucket %s: %s", bucket_name, data)

        if data is None or len(data) == 0:
            logger.warning("No data for bucket %s", bucket_name)
            return
    
    # Get the PoP-specific label for the given bucket_name
    label = settings.POP_BUCKET_LABELS.get(bucket_name, f"Unknown PoP in {bucket_name}")

    # Extract 'name' values from the collected data
    names = [item.get('name') for item in data]  # Extract 'name' using item.get('name')

    # Create a list to store unique building names to send
    names_to_send = []

    for name in names:
        # Check if data for this building name has already been sent
        if name and not is_data_sent(name) and name not in names_to_send:
            # Add the name to the list of names to send
            names_to_send.append(name)

            # Cache the building name if needed
            pop_cache_data(name)

    # Check if there are names to send
    if names_to_send:
        # Prepare the message text with comma-separated names
        message = ", ".join(names_to_send)

        # Send the message to the Lark webhook with the dynamic title
        send_lark_alert(message, label, settings.POP_WEBHOOK_URL)

    # Log the collected 'name' values and label for verification
    logger.info("Collected 'name' values: %s", names_to_send)
    logger.info("Label: %s", label)
####################################################################
@shared_task
def lark_post(bucket_name):
    global unique_names_sets  # Define the global dictionary

    # Initialize unique_names_sets as an empty dictionary if it doesn't exist
    if 'unique_names_sets' not in globals():
        unique_names_sets = {}

    # Fetch data using off_bldg from influx_utils.py
    data = off_bldg(bucket_name)

    # Check if data is None or empty
    if data is None or len(data) == 0:
        logger.warning("No data for bucket %s", bucket_name)
        return

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
        send_lark_alert(message, label, settings.LARK_WEBHOOK_URL)

    # Log the collected 'name' values and label for verification
    logger.info("Collected 'name' values: %s", unique_names_sets[bucket_name])
    logger.info("Label: %s", label)