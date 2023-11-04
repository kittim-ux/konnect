import json
import logging
from celery import shared_task
from .influx_utils import off_bldg, pop_monitor
from .cache_bldgs import is_data_sent, cache_data, pop_cache_data
import requests
from django.conf import settings
import datetime

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

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

    # Initialize data as an empty list
    #data = []


    # Check if the bucket_name is in the POP_BUCKET_MAPPING
    if bucket_name in settings.POP_BUCKET_MAPPING:
        # Fetch data using a function specific to PoP power outages
        data = pop_monitor(bucket_name)
        print(bucket_name)
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

###################################################################################
#GPON MONITORING
# Define a cache dictionary to store building names, ONUs count, and their last alert timestamp
alert_cache = {}

def gpon_alert(message, region):
    """
    Sends an alert message with the list of offline buildings.

    Args:
        message (str): A message string with offline building names and their total ONUs.
        region (str): The region associated with the offline buildings.
    """
    if message:
        # Get the label associated with the region from the mapping dictionary
        label = settings.GPON_BUCKET_LABELS.get(region, 'Unknown Region')

        # Split the message into lines and get the building names and ONUs count
        lines = message.split('\n')[2:]  # Skip the first two lines (header)
        building_info = [line.split('\t') for line in lines if line]

        # Check if any building name in the message has been alerted within the last 2 hours
        current_time = datetime.datetime.now()
        alert_building_info = []

        # Find the maximum length of the building names for formatting
        max_building_name_length = max(len(building) for building, onus in building_info)

        for building_name, onus_count in building_info:
            last_alert_time = alert_cache.get(building_name)

            if last_alert_time is None or (current_time - last_alert_time).total_seconds() >= 7200:
                # Either building name hasn't been alerted before or cache has expired (2 hours)
                alert_building_info.append((building_name, onus_count))
                # Update the cache with the current time
                alert_cache[building_name] = current_time

        # If there are building names to alert, send the message
        if alert_building_info:
            # Prepare the filtered message with building names and ONUs count with adjusted padding
            filtered_message = "Name" + ' ' * (max_building_name_length - 4) + "\tONUs\n" + \
                              "\n".join(f"{building}{(' ' * (max_building_name_length - len(building)))}\t{onus}"
                                        for building, onus in alert_building_info)

            # Send the filtered message to the Lark webhook with the dynamic title
            send_lark_alert(filtered_message, label, settings.GPON_WEBHOOK_URL)

            # Log the collected building names and label for verification
            logger.info("Collected offline buildings: %s", filtered_message)
            logger.info("Label: %s", label)




