from rest_framework import serializers
from .models import ConnectedTVs
#from django.contrib.auth.models Connected.TVs
#converting Django models to JSON objects and vice-versa for frontend to work with recieved data

class TvSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedTVs
        fields = ('__all__')