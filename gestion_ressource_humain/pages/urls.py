from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Racine
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('about/', views.about, name='about'),
    path('navbar/', views.navbar, name='navbar'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('joboffer/', views.joboffer, name='joboffer'),
    path('logout/', views.logout_view, name='logout'),
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
    path('trainings/', views.trainings, name='trainings'),
    path('rh_trainings/', views.rh_trainings, name='rh_trainings'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='html_of_pages/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='html_of_pages/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('contact_messages', views.contact_messages, name='contact_messages')
]