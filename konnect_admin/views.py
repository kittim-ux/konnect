import json
from pickle import FALSE
from rest_framework import generics, response, status
from .serializers import TvSerializer
from django.views import generic
from rest_framework.decorators import api_view
from .models import ConnectedTVs
from django.http import JsonResponse
from influxdb import InfluxDBClient



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


#Collect Data from Influx
client = InfluxDBClient(host='localhost', port=8086)