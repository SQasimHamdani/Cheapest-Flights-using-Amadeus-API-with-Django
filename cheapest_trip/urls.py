from django.urls import path 
from . import views 

urlpatterns = [ 
    path('', views.home, name='home'), 
    path('search', views.search, name='search'), 
    path('arrival_cities_loader', views.arrival_cities_loader, name='arrival_cities_loader'), 
    path('departure_cities_loader', views.departure_cities_loader, name='departure_cities_loader'), 
    path('update_flights_record', views.update_flights_record, name='update_flights_record'), 
] 