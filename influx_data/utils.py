from datetime import datetime, timedelta
from elasticsearch import Elasticsearch


def extract_gpon_port(if_descr):
    # Extract the gpon_port from if_descr, assuming it follows the format "GPONx/y:z"
    parts = if_descr.split(':')
    if len(parts) == 2:
        return parts[0].split('/')[-1].strip()  # Return the part before the colon
    return "N/A"

def extract_olt_number(agent_host):
    # Hardcoded IP-OLT mappings to match the correct OLTs for SUNTON
    hardcoded_mappings = {
        "10.103.0.1": 5,
        "10.103.0.2": 6,
        "10.103.0.3": 7,
        "10.103.0.4": 8,
        # Add more mappings as needed
    }

    # Check if the IP is in the hardcoded mappings
    if agent_host in hardcoded_mappings:
        return hardcoded_mappings[agent_host]
    # Extract the olt_number from agent_host, assuming it's an IP address like "10.x.y.z"
    parts = agent_host.split('.')
    if len(parts) == 4:
        return int(parts[-1])  # Assuming the olt_number is the last part of the IP address
    return "N/A"

#ElasticSearch utils to handle ONUs that have not been confirmed 