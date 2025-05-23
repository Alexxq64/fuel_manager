from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('fuel-arrival/', views.fuel_arrival, name='fuel_arrival'),
    path('refuel/', views.refuel, name='refuel'),
    path('ajax/get_price/', views.get_price_for_nozzle, name='get_price_for_nozzle'),
    path('statistics/', views.statistics_view, name='statistics'),
]
