from django.urls import path 
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),  # http://127.0.0.1:8000/pages/index/
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
]