from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('create/', views.create_item, name='create_item'),
    path('claim/<int:item_id>/', views.submit_claim, name='submit_claim'),
    path('approve/<int:claim_id>/', views.approve_claim, name='approve_claim'),
    path('reject/<int:claim_id>/', views.reject_claim, name='reject_claim'),
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('match-feedback/<int:match_id>/<str:feedback>/', views.match_feedback, name='match_feedback'),
    # we can add claims, profile, etc., later
]