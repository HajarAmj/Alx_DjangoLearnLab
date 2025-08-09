from django.urls import path
from . import views

urlpatterns = [
    # Example URL pattern, change to your actual view
    path('', views.index, name='index'),
]
