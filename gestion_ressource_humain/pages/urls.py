from django.urls import path 
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),  # http://127.0.0.1:8081/pages/index/ mais pour docker : http://127.0.0.1:8081/pages/index/
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
    path('navbar/', views.navbar, name='navbar'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('joboffer/', views.joboffer, name='joboffer'),
    path('sidebar/', views.sidebar, name='sidebar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('departments/', views.departments, name='departments'),
    path('employees/', views.employees, name='employees'),
    path('contracts/', views.contracts, name='contracts'),
    path('performance/', views.performance, name='performance'),
    path('joboffer_dashboard/', views.joboffer_dashboard, name='joboffer_dashboard'),
    path('candidates/', views.candidates, name='candidates'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('utulisateurs/', views.utulisateurs, name='utulisateurs'),
]