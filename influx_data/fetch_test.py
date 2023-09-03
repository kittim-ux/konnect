from elasticsearch import Elasticsearch
import time

# Define the Elasticsearch URL
es = Elasticsearch('http://localhost:9200')

# Specify the Elasticsearch index you want to retrieve data from
index_name = 'stnbucket'

# Keep track of the last document's timestamp
last_timestamp = None

# Continuously query and print new documents
while True:
    # Define a search query to retrieve documents with a timestamp greater than the last timestamp
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gt": last_timestamp
                }
            }
        }
    }

    # Use the Elasticsearch search method to execute the query
    response = es.search(index=index_name, body=query)

    # Print the retrieved documents
    for hit in response['hits']['hits']:
        print(hit['_source'])
        # Update the last timestamp
        last_timestamp = hit['_source']['timestamp']

    # Sleep for a while before querying again (adjust the sleep duration as needed)
    time.sleep(60)  # Sleep for 60 seconds before the next query

