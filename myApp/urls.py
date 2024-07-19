from django.urls import path
from . import views


urlpatterns = [
    path('', views.home.as_view(), name="home"),
    #path('progress/', views.get_download_progress, name='get_download_progress'),
]
