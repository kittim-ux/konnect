import os
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Initialize the Elasticsearch client
es_host = os.getenv('ELASTICSEARCH_HOST')
es_port = int(os.getenv('ELASTICSEARCH_PORT'))
es_scheme = os.getenv('ELASTICSEARCH_SCHEME')
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': es_scheme}])

# Define a mapping of bucket names to Elasticsearch index names
BUCKET_INDEX_MAP = {
    'STNOnu': 'stnbucket',
    'MWKs': 'mwks',
    'MWKn': 'mwkn',
    'KWDOnu': 'kwd',
    'KSNOnu': 'ksn',
}

def index_data(bucket, data):
    try:
        documents = []
        elasticsearch_index = BUCKET_INDEX_MAP.get(bucket, None)

        if elasticsearch_index:
            # Check if the index exists, and if not, create it
            if not es.indices.exists(index=elasticsearch_index):
                # Define the index settings and mappings here if needed
                # You can also use Elasticsearch index templates for more complex mappings
                es.indices.create(index=elasticsearch_index)

            for entry in data:
                # Validate data before indexing (e.g., check required fields)

                document = {
                    'bucket': entry['bucket'],
                    'ifDescr': entry['ifDescr'],
                    'serialNumber': entry['serialNumber'],
                    'ifOperStatus': entry['ifOperStatus'],
                    'agent_host': entry['agent_host'],
                    'influx_timestamp': entry['influx_timestamp'],
                    'elastic_timestamp': entry['elastic_timestamp'],
                }
                json_document = json.dumps(document)
                documents.append(json_document)

            # Bulk indexing
            bulk(es, documents, index=elasticsearch_index)

            # Force an index refresh
            es.indices.refresh(index=elasticsearch_index)

            print(f"Data indexed into Elasticsearch for {bucket} successfully.")
    except Exception as e:
        print(f"Error indexing data for {bucket} into Elasticsearch: {str(e)}")

