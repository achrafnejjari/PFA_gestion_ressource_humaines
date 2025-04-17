from django.urls import path 
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),  # http://127.0.0.1:8000/pages/index/ mais pour docker : http://127.0.0.1:8081/pages/index/
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
    path('navbar/', views.navbar, name='navbar'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('joboffer/', views.joboffer, name='joboffer'),
]