from django.urls import path
from . import views

urlpatterns = [
    path('', views.transcribe_video, name='transcribe_video'),
    path('status/<str:task_id>/', views.transcription_status, name='transcription_status'),

]