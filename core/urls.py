from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('create/', views.create_item, name='create_item'),
    # we can add claims, profile, etc., later
]