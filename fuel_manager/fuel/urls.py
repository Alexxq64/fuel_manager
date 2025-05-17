from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # главная страница будет показывать views.home
    path('fuel-arrival/', views.fuel_arrival, name='fuel_arrival'),
    path('refuel/', views.refuel, name='refuel'),
]
