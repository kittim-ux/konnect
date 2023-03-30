import csv
import os
import json
from pickle import FALSE
from django.shortcuts import render
from rest_framework import generics, response, status
from .serializers import TvSerializer
from django.views import generic
from django.views.generic import View
from rest_framework.decorators import api_view
from .models import ConnectedTVs
from django.http import JsonResponse
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
from rest_framework.views import APIView


#Dispaly TVs' Data. 
class ConnectedTVsListView(generics.ListAPIView):
    queryset = ConnectedTVs.objects.all()
    serializer_class = TvSerializer

    def list(self, request):
        tvs = self.get_queryset()
        serializer = self.get_serializer(tvs, many=True)
        return response.Response(serializer.data)

class ConnectedTVsDetailView(generics.RetrieveAPIView):
    queryset = ConnectedTVs.objects.all()
    serializer_class = TvSerializer
    lookup_field = 'id'
    
    def put(self, request, *args, **kwags):
        connected_tv = self.get_object()
        serializer = TvSerializer(connected_tv, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, slug):
        connected_tv = self.get_object()
        serializer = self.get_serializer(connected_tv)
        if connected_tv:
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return response.Response('TV Not found!', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, slug):
        connected_tv = self.get_object()
        connected_tv.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


#COLLECT ALL BUILDINGS DATA FROM INFLUX
class InfluxDataView(APIView):
    load_dotenv()
    
    CSV_BUCKET_MAP = {
            'kwtbucket': 'kwtbldg.csv',
            'g44bucket': 'g44bldg.csv',
            'zmmbucket': 'zmmbldg.csv',
            'RMM': 'rmmbldg.csv',
            'G45NBucket': 'g45nbldg.csv'
        }
    BUCKET_HOST_MAP = {
            'kwtbucket': 'KWT-FIBER',
            'g44bucket': 'G44-FIBER',
            'zmmbucket': 'ZMM-FIBER',
            'zmmbucket': 'ROY-FIBER',
            'G45NBucket': 'G45N-FIBER'
        }
    token = os.getenv('token')
    org = os.getenv('org')
    url = os.getenv('url')

    def off_bldg(self, bucket, token=token, org=org, url=url): 
        influx_client = InfluxDBClient(url="http://app.sasakonnect.net:8086", token="Sj2kYgP81WjQs_PFBnUmOB4qtgJtpzbmvE-1M1i3uCI0x9wCQOIFMAwezoTb7roY-p1S3NcpIXt2yt1-SEPrmQ==", org="AH")
        

        dataset_dir = '/home/ahdaniel/projects/buildingservices/konnect/influx_data/datasets'
        

        with open(os.path.join(dataset_dir, self.CSV_BUCKET_MAP[bucket]), "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            names = [row[0] for row in reader]

        all_results = []
        for name in names:
            query_string = f"""from(bucket: "{bucket}")
                |> range(start: -1m)
                |> filter(fn: (r) => r["_measurement"] == "ping")
                |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
                |> filter(fn: (r) => r["host"] == "{self.BUCKET_HOST_MAP[bucket]}")
                |> filter(fn: (r) => r["name"] == "{name}")
                |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
                |> yield(name: "mean")"""
            results = influx_client.query_api().query(query_string)
            
            data = []
            for table in results:
                for record in table.records:
                    if record.get_value() == 100:
                        data.append({
                            'name': record.values["name"],
                            'value': record.get_value(),
                            'field': record.get_field(),
                            'measurement': record.get_measurement()
                        })
            all_results += data
        return all_results

    def get(self, request):
        bucket = request.query_params.get('bucket', None)
        if not bucket:
            return JsonResponse({"error": "Data not defined yet"})
        else:
            all_results = self.off_bldg(bucket)
            return JsonResponse(all_results, safe=False)

#COLLECT DATA FOR A SINGLE BUILDING 
class InfluxBldgView(APIView):
    load_dotenv()
    
    CSV_BUCKET_MAP = {
        'kwtbucket': {'csv_file': 'kwtbldg.csv', 'bucket': 'kwtbucket'},
        'g44bucket': {'csv_file': 'g44bldg.csv', 'bucket': 'g44bucket'},
        'zmmbucket': {'csv_file': 'zmmbldg.csv', 'bucket': 'zmmbucket'},
        'RMM': {'csv_file': 'rmmbldg.csv', 'bucket': 'RMM'},
        'G45NBucket': {'csv_file': 'g45nbldg.csv', 'bucket': 'G45NBucket'},
        'G45SBucket': {'csv_file': 'g45sbldg.csv', 'bucket': 'G45SBucket'},
        'LsmBucket': {'csv_file': 'lsmbldg.csv', 'bucket': 'LsmBucket'},
        'htrbucket': {'csv_file': 'htrbldg.csv', 'bucket': 'htrbucket'},
    }

    BUCKET_HOST_MAP = {
        'kwtbucket': 'KWT-FIBER',
        'g44bucket': 'G44-FIBER',
        'zmmbucket': 'ZMM-FIBER',
        'RMM': 'ROY-FIBER',
        'G45NBucket': 'G45N-FIBER',
        'G45SBucket': 'G45-FIBER',
        'LsmBucket': 'LSM-FIBER',
        'htrbucket': 'HTR-FIBER',
    }

    token = os.getenv('token')
    org = os.getenv('org')
    url = os.getenv('url')

    def off_bldg(self, bucket, building_name, token=token, org=org, url=url):
        if bucket not in self.CSV_BUCKET_MAP:
            return JsonResponse({"error": f"{bucket} not found in CSV_BUCKET_MAP"})
        csv_file = self.CSV_BUCKET_MAP[bucket]['csv_file']
        bucket = self.CSV_BUCKET_MAP[bucket]['bucket']
        
        dataset_dir = '/home/ahdaniel/projects/buildingservices/konnect/influx_data/datasets'

        # Check if the building name exists in the specified CSV file
        with open(os.path.join(dataset_dir, csv_file), "r") as f:
            reader = csv.reader(f)
            headers = next(reader)
            building_names = [row[0] for row in reader]

        if building_name not in building_names:
            return JsonResponse({"error": f"{building_name} not found in {csv_file}"})

        # Run the InfluxDB query only if the building name exists in the specified CSV file
        query_string = f"""from(bucket: "{bucket}")
            |> range(start: -1m)
            |> filter(fn: (r) => r["_measurement"] == "ping")
            |> filter(fn: (r) => r["_field"] == "percent_packet_loss")
            |> filter(fn: (r) => r["host"] == "{self.BUCKET_HOST_MAP[bucket]}")
            |> filter(fn: (r) => r["name"] == "{building_name}")
            |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
            |> yield(name: "mean")"""

        influx_client = InfluxDBClient(url="http://127.0.0.1:8086", token="Sj2kYgP81WjQs_PFBnUmOB4qtgJtpzbmvE-1M1i3uCI0x9wCQOIFMAwezoTb7roY-p1S3NcpIXt2yt1-SEPrmQ==", org="AH")
        results = influx_client.query_api().query(query_string)

        data = []
        for table in results:
            for record in table.records:
                    data.append({
                        'name': record.values["name"],
                        'value': record.get_value(),
                        'field': record.get_field(),
                        'measurement': record.get_measurement()
                    })

        if not data:
            return JsonResponse({"error": f"No data found for {building_name}"})

        return JsonResponse(data, safe=False)

    def get(self, request):
        bucket = request.query_params.get('bucket', None)
        building_name = request.query_params.get('building_name', None)
        if not bucket or not building_name:
            return JsonResponse({"error": "Bucket and building_name are required parameters"})
        else:
            return self.off_bldg(bucket, building_name)