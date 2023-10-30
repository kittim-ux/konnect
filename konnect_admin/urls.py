from django.urls import path, include
from rest_framework import routers
from . import views
from konnect_admin.views import InfluxDataView, InfluxBldgView

router = routers.DefaultRouter()

# The url path for the API
urlpatterns = [
    path('off_buildings/', views.InfluxDataView.as_view(), name='off_buildings'),
    path('influxbldgview/', views.InfluxBldgView.as_view(), name='bldg_data'),
]

# Comment out or remove the following line since it's not used in your current configuration
# router.register(r'connected_tvs', views.ConnectedTVsDetailView, basename='connected_tvs')