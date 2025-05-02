from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Utilisateur, Role, Employe, Performance, Departement, Contrat, Conge, EmployeConge, Training, TrainingRegistration
from datetime import date

# Décorateur personnalisé pour vérifier si l'utilisateur est RH
def rh_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.utilisateur.role.nom_role != 'RH':
            return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return view_func(request, *args, **kwargs)
    return wrapper

# Pages principales
def index(request):
    return render(request, 'html_of_pages/index.html', {'active_page': 'index'})

# Connexion au site web
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Vérifier les identifiants
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Les identifiants sont corrects, connecter l'utilisateur
            login(request, user)
            return redirect('index')  # Redirige vers la page d'accueil (index.html)
        else:
            # Identifiants incorrects, afficher un message d'erreur
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return redirect('login')

    return render(request, 'html_of_pages/login.html', {'active_page': 'login'})

def about(request):
    return render(request, 'html_of_pages/about.html', {'active_page': 'about'})

def navbar(request):
    return render(request, 'html_of_pages/navbar.html', {'active_page': 'navbar'})

# Créer utilisateur
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        photo = request.FILES.get('photo')

        # Validation des données
        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('signup')

        # Vérifier si le nom d'utilisateur ou l'email existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('signup')

        # Créer l'utilisateur Django
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de l'utilisateur : {str(e)}")
            return redirect('signup')

        # Créer ou récupérer le rôle "Utilisateur" par défaut
        role, created = Role.objects.get_or_create(nom_role="Utilisateur")

        # Gérer la photo (si fournie)
        photo_url = None
        if photo:
            fs = FileSystemStorage()
            filename = fs.save(f'photos/{photo.name}', photo)
            photo_url = fs.url(filename)

        # Créer l'objet Utilisateur
        utilisateur = Utilisateur.objects.create(
            user=user,
            role=role,
            url_photo=photo_url if photo_url else ''
        )

        messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'html_of_pages/signup.html', {'active_page': 'signup'})

def contact(request):
    return render(request, 'html_of_pages/contact.html', {'active_page': 'contact'})

def services(request):
    return render(request, 'html_of_pages/services.html', {'active_page': 'services'})

def joboffer(request):
    return render(request, 'html_of_pages/joboffer.html', {'active_page': 'joboffer'})

# Dashboard
def sidebar(request):
    return render(request, 'html_of_pages/dashboard/sidebar.html', {'active_page': 'sidebar'})

# Accés aux pages dashboard
@login_required
def dashboard(request):
    role = request.user.utilisateur.role.nom_role

    if role == 'RH':
        # Dashboard pour RH (liste de tous les employés)
        employees = Employe.objects.all()
        employees_data = []
        
        for employee in employees:
            today = date.today()
            years_of_service = today.year - employee.date_embauche.year
            if today.month < employee.date_embauche.month or (today.month == employee.date_embauche.month and today.day < employee.date_embauche.day):
                years_of_service -= 1

            performance = Performance.objects.filter(employe=employee).order_by('-date_evaluation').first()
            performance_score = f"{performance.score}%" if performance else "N/A"

            employees_data.append({
                'nom': employee.nom,
                'prenom': employee.prenom,
                'email': employee.email,
                'telephone': employee.telephone,
                'salaire': f"{employee.salaire_actuel}€",
                'departement': employee.departement.nom if employee.departement else "Non spécifié",
                'anciennete': f"{years_of_service} an{'s' if years_of_service != 1 else ''}",
                'performance': performance_score,
                'date_embauche': employee.date_embauche.strftime('%d/%m/%Y'),
                'date_fin': employee.date_fin.strftime('%d/%m/%Y') if employee.date_fin else "-",
                'statut': employee.contrat.type if employee.contrat else "N/A",
            })

        return render(request, 'html_of_pages/dashboard/dashboard.html', {
            'active_page': 'dashboard',
            'employees_data': employees_data,
        })

    elif role == 'Employé':
        # Dashboard pour Employé (informations personnelles)
        try:
            utilisateur = request.user.utilisateur
            employee = Employe.objects.get(utilisateur=utilisateur)
            today = date.today()
            years_of_service = today.year - employee.date_embauche.year
            if today.month < employee.date_embauche.month or (today.month == employee.date_embauche.month and today.day < employee.date_embauche.day):
                years_of_service -= 1

            performance = Performance.objects.filter(employe=employee).order_by('-date_evaluation').first()
            recent_performances = Performance.objects.filter(employe=employee).order_by('-date_evaluation')[:3]

            employee_data = {
                'nom': employee.nom,
                'prenom': employee.prenom,
                'email': employee.email,
                'telephone': employee.telephone,
                'salaire': f"{employee.salaire_actuel}€",
                'departement': employee.departement.nom if employee.departement else "Non spécifié",
                'anciennete': f"{years_of_service} an{'s' if years_of_service != 1 else ''}",
                'performance': f"{performance.score}%" if performance else "N/A",
                'date_embauche': employee.date_embauche.strftime('%d/%m/%Y'),
                'date_fin': employee.date_fin.strftime('%d/%m/%Y') if employee.date_fin else "-",
                'statut': employee.contrat.type if employee.contrat else "N/A",
            }

            return render(request, 'html_of_pages/dashboard/employee_dashboard.html', {
                'active_page': 'dashboard',
                'employee_data': employee_data,
                'recent_performances': recent_performances,
            })
        except Employe.DoesNotExist:
            
            return render(request, 'html_of_pages/dashboard/employee_dashboard.html', {
                'active_page': 'dashboard',
                'employee_data': None,
                'recent_performances': [],
            })

    else:
        # Dashboard pour Utilisateur
        return render(request, 'html_of_pages/dashboard/user_dashboard.html', {
            'active_page': 'dashboard',
        })

@login_required
@rh_required
def departments(request):
    return render(request, 'html_of_pages/dashboard/departments.html', {'active_page': 'departments'})

@login_required
@rh_required
def employees(request):
    return render(request, 'html_of_pages/dashboard/employees.html', {'active_page': 'employees'})

@login_required
@rh_required
def contracts(request):
    return render(request, 'html_of_pages/dashboard/contracts.html', {'active_page': 'contracts'})

@login_required
@rh_required
def performance(request):
    return render(request, 'html_of_pages/dashboard/performance.html', {'active_page': 'performance'})

# Dashboard: Employé
@login_required
def employee_performance(request):
    if request.user.utilisateur.role.nom_role != 'Employé':
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    try:
        utilisateur = request.user.utilisateur
        employee = Employe.objects.get(utilisateur=utilisateur)
        performances = Performance.objects.filter(employe=employee).order_by('-date_evaluation')
        return render(request, 'html_of_pages/dashboard/employee_performance.html', {
            'active_page': 'employee_performance',
            'performances': performances,
        })
    except Employe.DoesNotExist:
        messages.error(request, "Aucun profil employé associé à votre compte. Veuillez contacter un administrateur.")
        return render(request, 'html_of_pages/dashboard/employee_performance.html', {
            'active_page': 'employee_performance',
            'performances': [],
        })

@login_required
def leave_requests(request):
    if request.user.utilisateur.role.nom_role != 'Employé':
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    try:
        utilisateur = request.user.utilisateur
        employee = Employe.objects.get(utilisateur=utilisateur)
        employee_conges = EmployeConge.objects.filter(employe=employee).order_by('-conge__created_at')

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason', 'Congé annuel')

            conge = Conge.objects.create(
                type=reason,
                date_debut=start_date,
                date_fin=end_date,
                statut='EN_ATTENTE'
            )

            EmployeConge.objects.create(
                employe=employee,
                conge=conge
            )

            messages.success(request, "Votre demande de congé a été soumise avec succès !")
            return redirect('leave_requests')

        return render(request, 'html_of_pages/dashboard/leave_requests.html', {
            'active_page': 'leave_requests',
            'employee_conges': employee_conges,
            'employee': employee,
        })
    except Employe.DoesNotExist:
        return render(request, 'html_of_pages/dashboard/leave_requests.html', {
            'active_page': 'leave_requests',
            'employee_conges': [],
        })
    
@login_required
@rh_required
def joboffer_dashboard(request):
    return render(request, 'html_of_pages/dashboard/joboffer_dashboard.html', {'active_page': 'joboffer_dashboard'})

@login_required
def user_joboffers(request):
    if request.user.utilisateur.role.nom_role not in ['Utilisateur', 'Employé']:
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    # Liste fictive d'offres d'emploi (à remplacer par un modèle JobOffer plus tard)
    job_offers = [
        {'title': 'Développeur Python', 'department': 'Informatique', 'type': 'CDI', 'posted_date': '2025-04-01'},
        {'title': 'Responsable Marketing', 'department': 'Marketing', 'type': 'CDD', 'posted_date': '2025-04-15'},
        {'title': 'Assistant RH', 'department': 'Ressources Humaines', 'type': 'CDI', 'posted_date': '2025-04-20'},
    ]

    return render(request, 'html_of_pages/dashboard/user_joboffers.html', {
        'active_page': 'user_joboffers',
        'job_offers': job_offers,
    })

@login_required
@rh_required
def candidates(request):
    return render(request, 'html_of_pages/dashboard/candidates.html', {'active_page': 'candidates'})

@login_required
def profile(request):
    utilisateur = request.user.utilisateur
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            fs = FileSystemStorage()
            filename = fs.save(f'photos/{photo.name}', photo)
            photo_url = fs.url(filename)
            utilisateur.url_photo = photo_url
            utilisateur.save()
        return redirect('profile')
    return render(request, 'html_of_pages/dashboard/profile.html', {'active_page': 'profile', 'utilisateur': utilisateur})

@login_required
def settings(request):
    return render(request, 'html_of_pages/dashboard/settings.html', {'active_page': 'settings'})

@login_required
@rh_required
def utilisateurs(request):
    return render(request, 'html_of_pages/dashboard/utilisateurs.html', {'active_page': 'utilisateurs'})

# Training views
@login_required
def trainings(request):
    if request.user.utilisateur.role.nom_role != 'Employé':
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    try:
        # Récupérer l'utilisateur connecté
        utilisateur = request.user.utilisateur
        # Récupérer l'employé lié à cet utilisateur
        employee = Employe.objects.get(utilisateur=utilisateur)
        # Récupérer toutes les formations disponibles
        trainings = Training.objects.all().order_by('-created_at')
        # Récupérer les formations auxquelles l'employé est inscrit
        registered_trainings = TrainingRegistration.objects.filter(employee=employee).values_list('training_id', flat=True)

        if request.method == 'POST':
            training_id = request.POST.get('training_id')
            training = Training.objects.get(id=training_id)
            TrainingRegistration.objects.create(employee=employee, training=training)
            messages.success(request, "Vous êtes inscrit à la formation avec succès !")
            return redirect('trainings')

        return render(request, 'html_of_pages/dashboard/trainings.html', {
            'active_page': 'trainings',
            'trainings': trainings,
            'registered_trainings': registered_trainings,
        })
    except Employe.DoesNotExist:
        
        return render(request, 'html_of_pages/dashboard/trainings.html', {
            'active_page': 'trainings',
            'trainings': [],
            'registered_trainings': [],
        })
    
@login_required
def rh_trainings(request):
    if request.user.utilisateur.role.nom_role != 'RH':
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    trainings = Training.objects.all().order_by('-created_at')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        Training.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date
        )
        return redirect('rh_trainings')

    return render(request, 'html_of_pages/dashboard/rh_trainings.html', {
        'active_page': 'rh_trainings',
        'trainings': trainings,
    })

def logout_view(request):
    logout(request)
    return redirect('login')