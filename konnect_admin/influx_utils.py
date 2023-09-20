import os
import csv
from pathlib import Path
from influxdb import InfluxDBClient
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

# Load environment variables from the .env file
dotenv_path = Path('/home/kitim/projects/konnect-app/konnect/influx_data/.env')
load_dotenv(dotenv_path=dotenv_path)

# Define the CSV_BUCKET_MAP and BUCKET_HOST_MAP
CSV_BUCKET_MAP = {
    'kwtbucket': 'kwtbldg.csv',
    'g44bucket': 'g44bldg.csv',
    'zmmbucket': 'zmmbldg.csv',
    'RMM': 'rmmbldg.csv',
    'G45N1Bucket': 'g45nbldg.csv',
    'G45SBucket': 'g45sbldg.csv',
    'LsmBucket': 'lsmbldg.csv',
    'htrbucket': 'htrbldg.csv',
}
BUCKET_HOST_MAP = {
    'kwtbucket': 'KWT-FIBER',
    'g44bucket': 'G44-FIBER',
    'zmmbucket': 'ZMM-FIBER',
    'RMM': 'ROY-FIBER',
    'G45SBucket': 'G45-FIBER',
    'G45N1Bucket': 'G45N-FIBER',
    'LsmBucket': 'LSM-FIBER',
    'htrbucket': 'HTR-FIBER',
}

def off_bldg(bucket):
    dataset_dir = '/home/kitim/projects/konnect-app/konnect/influx_data/datasets'
    token = os.getenv('token')
    org = os.getenv('org')
    url = os.getenv('url')

    client = InfluxDBClient(url=url, token=token, org=org)

    with open(os.path.join(dataset_dir, CSV_BUCKET_MAP.get(bucket, '')), "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        names = [row[0] for row in reader if len(row) > 0]  # Filter out empty rows

    all_results = []
    for name in names:
        query_string = f"""from(bucket: "{bucket}")
            |> range(start: -10m)
            |> filter(fn: (r) => r["_measurement"] == "ping")
            |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
            |> filter(fn: (r) => r["host"] == "{BUCKET_HOST_MAP.get(bucket, '')}")
            |> filter(fn: (r) => r["name"] == "{name}")
            |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
            |> yield(name: "mean")"""
        results = client.query_api().query(query_string)

        data = []
        for table in results:
            for record in table.records:
                if record.get_value() == 100:
                    data.append({
                        'name': record.values.get("name", ''),
                        'value': record.get_value(),
                        'field': record.get_field(),
                        'measurement': record.get_measurement()
                    })
        all_results += data
    return all_results
