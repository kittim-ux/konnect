from django.urls import path, include
from rest_framework import routers
from . import views
from konnect_admin.views import ConnectedTVsListView, ConnectedTVsDetailView, InfluxDataView, InfluxBldgView, NewModelView


router = routers.DefaultRouter()

#router.register(r'home', homeViewSet, basename='user')

#The url path for the API
urlpatterns = [
    path('connectedtvs/', ConnectedTVsListView.as_view(), name='connected_tvs'),
    path('connectedtvs/<int:id>/', ConnectedTVsDetailView.as_view(), name='connected_tv_detail'),
    path('off_buildings/', views.InfluxDataView.as_view(), name='off_buildings'),
    path('influxbldgview/', views.InfluxBldgView.as_view(), name='bldg_data'),
    path('newmodelview/', views.NewModelView.as_view(), name='onu_data'),
]
