from django.urls import path 
from . import views

urlpatterns = [
    # Racine
    path('', views.index, name='index'),  # Ajout de la racine

    # Pages principales
    path('index/', views.index, name='index'),  # http://127.0.0.1:8081/pages/index/
    path('login/', views.login_view, name='login'),
    path('about/', views.about, name='about'),  # Suppression du duplicata
    path('navbar/', views.navbar, name='navbar'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('joboffer/', views.joboffer, name='joboffer'),
    path('logout/', views.logout_view, name='logout'),  # Ajout pour navbar.html

    # Dashboard
    path('sidebar/', views.sidebar, name='sidebar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('departments/', views.departments, name='departments'),
    path('employees/', views.employees, name='employees'),
    path('contracts/', views.contracts, name='contracts'),
    path('performance/', views.performance, name='performance'),
    path('joboffer_dashboard/', views.joboffer_dashboard, name='joboffer_dashboard'),
    path('candidates/', views.candidates, name='candidates'),
    path('employee_performance/', views.employee_performance, name='employee_performance'),
    path('leave_requests/', views.leave_requests, name='leave_requests'),
    path('user_joboffers/', views.user_joboffers, name='user_joboffers'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('utilisateurs/', views.utilisateurs, name='utilisateurs'),
    path('trainings/', views.trainings, name='trainings'),  # Page pour les employés
    path('rh_trainings/', views.rh_trainings, name='rh_trainings'),  # Nouvelle page pour les RH
]