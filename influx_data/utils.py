from datetime import datetime, timedelta
from elasticsearch import Elasticsearch


def extract_gpon_port(if_descr):
    # Extract the gpon_port from if_descr, assuming it follows the format "GPONx/y:z"
    parts = if_descr.split(':')
    if len(parts) == 2:
        return parts[0].split('/')[-1].strip()  # Return the part before the colon
    return "N/A"

def extract_olt_number(agent_host):
    # Extract the olt_number from agent_host, assuming it's an IP address like "10.x.y.z"
    parts = agent_host.split('.')
    if len(parts) == 4:
        return int(parts[-1])  # Assuming the olt_number is the last part of the IP address
    return "N/A"

#ElasticSearch utils to handle ONUs that have not been confirmed 