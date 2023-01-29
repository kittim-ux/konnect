import json
from pickle import FALSE
from rest_framework import generics, response, status
from .serializers import TvSerializer
from django.views import generic
from .models import ConnectedTVs
from django.http import JsonResponse


# Create your views here.
class ConnectedTVsListView(generics.ListAPIView):
    queryset = ConnectedTVs.objects.all()
    serializer_class = TvSerializer
    

    def ConnectedTVsListView(request):
        tvs = ConnectedTVs.objects.all()
        tvs_list = [tv.to_json() for tv in tvs]
        return JsonResponse(tvs_list, safe=False)

class ConnectedTVsDetailView(generics.RetrieveAPIView):
    queryset = ConnectedTVs.objects.all()
    serializer_class = TvSerializer
    lookup_field = 'slug'

    def get(self, request, slug):
        connected_tv = self.get_object()
        serializer = TvSerializer(connected_tv)
        if connected_tv:
            if request.method == 'GET':
                return response.Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return response.Response('TV Not found!', status=status.HTTP_404_NOT_FOUND)