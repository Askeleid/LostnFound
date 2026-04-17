from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('create/', views.create_item, name='create_item'),
    path('claim/<int:item_id>/', views.submit_claim, name='submit_claim'),
    path('approve/<int:claim_id>/', views.approve_claim, name='approve_claim'),
    path('reject/<int:claim_id>/', views.reject_claim, name='reject_claim'),
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    # we can add claims, profile, etc., later
]