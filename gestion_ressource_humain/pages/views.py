from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Utilisateur, Role, Employe, Performance, Departement, Contrat, Conge, EmployeConge, Training, TrainingRegistration
from datetime import date
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.conf import settings

# Décorateur personnalisé pour vérifier si l'utilisateur est RH
def rh_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.utilisateur.role.nom_role != 'RH':
            return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return view_func(request, *args, **kwargs)
    return wrapper

# Surcharge de PasswordResetView pour déboguer
class CustomPasswordResetView(PasswordResetView):
    template_name = 'html_of_pages/password_reset.html'
    email_template_name = 'html_of_pages/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')
    from_email = settings.DEFAULT_FROM_EMAIL

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        print(f"Email reçu : {email}")
        try:
            user = User.objects.get(email=email)
            print(f"Utilisateur trouvé : {user.username}, is_active: {user.is_active}")
            if not user.is_active:
                user.is_active = True
                user.save()
                print("Utilisateur activé.")
        except User.DoesNotExist:
            print(f"Aucun utilisateur trouvé pour l'email {email}.")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print("Formulaire valide, préparation de l'envoi de l'email.")
        email = form.cleaned_data['email']
        users = User.objects.filter(email=email)
        for user in users:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            print(f"uidb64 généré : {uidb64}, token généré : {token}")

            # Préparer le contexte pour l'email
            context = {
                'user': user,
                'uidb64': uidb64,
                'token': token,
                'protocol': 'http',
                'domain': 'localhost:8081',  # Ajuste selon ton domaine
            }

            # Rendre le template d'email avec le contexte
            subject = 'Réinitialisation de votre mot de passe'
            message = render_to_string(self.email_template_name, context)
            send_mail(
                subject,
                message,
                self.from_email,
                [email],
                fail_silently=False,
                html_message=message,
            )
            print(f"Email envoyé à {email} avec uidb64={uidb64} et token={token}")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"Contexte passé au template : {context}")
        return context

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'html_of_pages/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    form_class = SetPasswordForm  # Utilisation explicite de SetPasswordForm

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
        print("Mot de passe réinitialisé avec succès.")
        return response

    def form_invalid(self, form):
        print(f"Erreurs du formulaire : {form.errors}")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'password_reset_confirm'
        return context
    
# Pages principales
def index(request):
    return render(request, 'html_of_pages/index.html', {'active_page': 'index'})

# Connexion au site web
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Récupérer la valeur de la case à cocher

        # Vérifier les identifiants
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Les identifiants sont corrects, connecter l'utilisateur
            login(request, user)

            # Gérer l'option "Se souvenir de moi"
            response = redirect('index')
            if remember_me:
                # Prolonger la session pour 2 semaines
                request.session.set_expiry(1209600)  # 2 semaines
                # Sauvegarder le nom d'utilisateur, le mot de passe, et l'indicateur "remember_me" dans des cookies
                response.set_cookie('username', username, max_age=1209600)  # 2 semaines
                response.set_cookie('password', password, max_age=1209600)  # 2 semaines
                response.set_cookie('remember_me', 'true', max_age=1209600)  # 2 semaines
            else:
                # Session par défaut : expire à la fermeture du navigateur
                request.session.set_expiry(0)
                # Ne pas supprimer les cookies ici, on le gérera dans logout_view
            return response
        else:
            # Identifiants incorrects, afficher un message d'erreur
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return redirect('login')

    # Récupérer les valeurs des cookies pour pré-remplir les champs
    username = request.COOKIES.get('username', '')
    password = request.COOKIES.get('password', '')
    remember_me_cookie = request.COOKIES.get('remember_me', 'false') == 'true'
    return render(request, 'html_of_pages/login.html', {
        'active_page': 'login',
        'username': username,
        'password': password,
        'remember_me': remember_me_cookie,  # Cocher la case si le cookie existe
    })

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
from datetime import date, timedelta

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

            # Calcul des jours de congé
            annual_leave_days = employee.contrat.leave_entitlement if employee.contrat and employee.contrat.leave_entitlement else 25
            employee_conges = EmployeConge.objects.filter(employe=employee)
            taken_days = 0
            for emp_conge in employee_conges:
                if emp_conge.conge.statut == 'APPROUVE':
                    delta = (emp_conge.conge.date_fin - emp_conge.conge.date_debut).days + 1  # Inclure le jour de fin
                    taken_days += delta

            remaining_days = annual_leave_days - taken_days

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
                'remaining_days': remaining_days,
                'taken_days': taken_days,
                'annual_leave_days': annual_leave_days,
            })
        except Employe.DoesNotExist:
            return render(request, 'html_of_pages/dashboard/employee_dashboard.html', {
                'active_page': 'dashboard',
                'employee_data': None,
                'recent_performances': [],
                'remaining_days': 0,
                'taken_days': 0,
                'annual_leave_days': 25,  # Valeur par défaut même en cas d'erreur
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
    if request.method == 'POST':
        action = request.POST.get('action')

        # Ajouter un employé
        if action == 'add_employee':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            utilisateur_id = request.POST.get('utilisateur_id')
            date_de_naissance = request.POST.get('date_de_naissance')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            salaire_actuel = request.POST.get('salaire_actuel')
            date_embauche = request.POST.get('date_embauche')
            date_fin = request.POST.get('date_fin', None)
            type_contrat = request.POST.get('type_contrat')
            departement_id = request.POST.get('departement')

            try:
                # Vérifier les doublons d'email
                if Employe.objects.filter(email=email).exists():
                    messages.error(request, "Cet email est déjà utilisé par un autre employé.")
                    return redirect('employees')

                # Créer un contrat
                contrat = Contrat.objects.create(
                    type=type_contrat,
                    date_debut=date_embauche,
                    date_fin=date_fin if date_fin else None,
                    salaire_initial=salaire_actuel
                )

                # Récupérer l'utilisateur à lier (si sélectionné)
                utilisateur = None
                if utilisateur_id:
                    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
                    # S'assurer que l'utilisateur n'est pas déjà lié à un autre employé
                    if Employe.objects.filter(utilisateur=utilisateur).exists():
                        messages.error(request, "Cet utilisateur est déjà lié à un autre employé.")
                        return redirect('employees')

                # Créer l'employé
                departement = Departement.objects.get(id=departement_id)
                Employe.objects.create(
                    nom=nom,
                    prenom=prenom,
                    utilisateur=utilisateur,
                    date_de_naissance=date_de_naissance,
                    email=email,
                    telephone=telephone,
                    salaire_actuel=salaire_actuel,
                    date_embauche=date_embauche,
                    date_fin=date_fin if date_fin else None,
                    contrat=contrat,
                    departement=departement
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'employé : {str(e)}")
            return redirect('employees')

        # Modifier un employé
        elif action == 'edit_employee':
            employee_id = request.POST.get('employee_id')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            utilisateur_id = request.POST.get('utilisateur_id')
            date_de_naissance = request.POST.get('date_de_naissance')
            email = request.POST.get('email')
            telephone = request.POST.get('telephone')
            salaire_actuel = request.POST.get('salaire_actuel')
            date_embauche = request.POST.get('date_embauche')
            date_fin = request.POST.get('date_fin', None)
            type_contrat = request.POST.get('type_contrat')
            departement_id = request.POST.get('departement')

            try:
                employee = Employe.objects.get(id=employee_id)

                # Vérifier les doublons d'email
                if Employe.objects.exclude(id=employee_id).filter(email=email).exists():
                    messages.error(request, "Cet email est déjà utilisé par un autre employé.")
                    return redirect('employees')

                # Mettre à jour l'utilisateur lié
                if utilisateur_id:
                    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
                    # Vérifier que l'utilisateur n'est pas déjà lié à un autre employé
                    if Employe.objects.exclude(id=employee_id).filter(utilisateur=utilisateur).exists():
                        messages.error(request, "Cet utilisateur est déjà lié à un autre employé.")
                        return redirect('employees')
                    employee.utilisateur = utilisateur
                else:
                    employee.utilisateur = None

                # Mettre à jour l'employé
                employee.nom = nom
                employee.prenom = prenom
                employee.date_de_naissance = date_de_naissance
                employee.email = email
                employee.telephone = telephone
                employee.salaire_actuel = salaire_actuel
                employee.date_embauche = date_embauche
                employee.date_fin = date_fin if date_fin else None
                employee.departement = Departement.objects.get(id=departement_id)
                employee.contrat.type = type_contrat
                employee.contrat.date_debut = date_embauche
                employee.contrat.date_fin = date_fin if date_fin else None
                employee.contrat.salaire_initial = salaire_actuel
                employee.contrat.save()
                employee.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'employé : {str(e)}")
            return redirect('employees')

        # Supprimer un employé
        elif action == 'delete_employee':
            employee_id = request.POST.get('employee_id')
            try:
                employee = Employe.objects.get(id=employee_id)
                employee.delete()
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de l'employé : {str(e)}")
            return redirect('employees')

        # Approuver ou rejeter un congé
        elif action in ['approve_leave', 'reject_leave']:
            conge_id = request.POST.get('conge_id')
            try:
                conge = Conge.objects.get(id=conge_id)
                conge.statut = 'APPROUVE' if action == 'approve_leave' else 'REFUSE'
                conge.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour du congé : {str(e)}")
            return redirect('employees')

        # Supprimer un congé
        elif action == 'delete_leave':
            conge_id = request.POST.get('conge_id')
            try:
                conge = Conge.objects.get(id=conge_id)
                conge.delete()
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression du congé : {str(e)}")
            return redirect('employees')

    # Statistiques
    total_employees = Employe.objects.count()
    departement_counts = {}
    for departement in Departement.objects.all():
        count = Employe.objects.filter(departement=departement).count()
        if count > 0:  # N'afficher que les départements avec des employés
            departement_counts[departement.nom] = count

    # Liste des utilisateurs avec le rôle "Employé" disponibles (ceux qui ne sont pas déjà liés à un employé)
    available_employe_users = Utilisateur.objects.filter(
        role__nom_role='Employé'
    ).exclude(
        employe__isnull=False
    )

    # Liste des employés
    employees_data = []
    for employee in Employe.objects.all():
        employees_data.append({
            'id': employee.id,
            'nom': employee.nom,
            'prenom': employee.prenom,
            'utilisateur_id': employee.utilisateur.id if employee.utilisateur else None,
            'utilisateur_username': employee.utilisateur.user.username if employee.utilisateur else None,
            'date_de_naissance': employee.date_de_naissance.strftime('%d/%m/%Y'),
            'email': employee.email,
            'telephone': employee.telephone,
            'salaire': f"{employee.salaire_actuel}€",
            'departement': employee.departement.nom if employee.departement else "Non spécifié",
            'departement_id': employee.departement.id if employee.departement else None,
            'date_embauche': employee.date_embauche.strftime('%d/%m/%Y'),
            'date_fin': employee.date_fin.strftime('%d/%m/%Y') if employee.date_fin else "-",
            'type_contrat': employee.contrat.type if employee.contrat else "N/A",
        })

    # Liste des congés
    leaves_data = []
    for employe_conge in EmployeConge.objects.all():
        leaves_data.append({
            'id': employe_conge.conge.id,
            'nom': f"{employe_conge.employe.nom}, {employe_conge.employe.prenom}",
            'type_conge': employe_conge.conge.type,
            'date_debut': employe_conge.conge.date_debut.strftime('%d/%m/%Y'),
            'date_fin': employe_conge.conge.date_fin.strftime('%d/%m/%Y'),
            'statut': employe_conge.conge.statut,
        })

    return render(request, 'html_of_pages/dashboard/employees.html', {
        'active_page': 'employees',
        'total_employees': total_employees,
        'departement_counts': departement_counts,
        'employees_data': employees_data,
        'leaves_data': leaves_data,
        'departements': Departement.objects.all(),
        'contrat_types': Contrat.TYPE_CHOICES,
        'available_employe_users': available_employe_users,  # Utilisateurs avec rôle "Employé" uniquement
    })

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
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Vérifier si un RH existe déjà
        rh_count = Utilisateur.objects.filter(role__nom_role='RH').count()

        # Ajouter un nouvel utilisateur
        if action == 'add':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            role_name = request.POST.get('role')
            photo = request.FILES.get('photo')

            # Validation
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return redirect('utilisateurs')
            if User.objects.filter(email=email).exists():
                messages.error(request, "Cet email est déjà utilisé.")
                return redirect('utilisateurs')
            # Vérifier la contrainte d'un seul RH
            if role_name == 'RH' and rh_count >= 1:
                messages.error(request, "Un utilisateur RH existe déjà. Vous ne pouvez pas en ajouter un autre.")
                return redirect('utilisateurs')

            # Créer l'utilisateur
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                role = Role.objects.get(nom_role=role_name)
                photo_url = None
                if photo:
                    fs = FileSystemStorage()
                    filename = fs.save(f'photos/{photo.name}', photo)
                    photo_url = fs.url(filename)

                Utilisateur.objects.create(
                    user=user,
                    role=role,
                    url_photo=photo_url if photo_url else ''
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'utilisateur : {str(e)}")
            return redirect('utilisateurs')

        # Modifier un utilisateur
        elif action == 'edit':
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            role_name = request.POST.get('role')
            photo = request.FILES.get('photo')

            try:
                user = User.objects.get(id=user_id)
                utilisateur = user.utilisateur

                # Vérifier les doublons
                if User.objects.exclude(id=user_id).filter(username=username).exists():
                    messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                    return redirect('utilisateurs')
                if User.objects.exclude(id=user_id).filter(email=email).exists():
                    messages.error(request, "Cet email est déjà utilisé.")
                    return redirect('utilisateurs')
                # Vérifier la contrainte d'un seul RH (sauf si l'utilisateur est déjà RH)
                if role_name == 'RH' and rh_count >= 1 and utilisateur.role.nom_role != 'RH':
                    messages.error(request, "Un utilisateur RH existe déjà. Vous ne pouvez pas en ajouter un autre.")
                    return redirect('utilisateurs')

                # Mettre à jour les informations
                user.username = username
                user.email = email
                user.save()

                utilisateur.role = Role.objects.get(nom_role=role_name)
                if photo:
                    fs = FileSystemStorage()
                    filename = fs.save(f'photos/{photo.name}', photo)
                    utilisateur.url_photo = fs.url(filename)
                utilisateur.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'utilisateur : {str(e)}")
            return redirect('utilisateurs')

        # Supprimer un utilisateur
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                # Ne pas supprimer le seul RH
                if user.utilisateur.role.nom_role == 'RH' and Utilisateur.objects.filter(role__nom_role='RH').count() <= 1:
                    messages.error(request, "Vous ne pouvez pas supprimer le seul utilisateur RH.")
                    return redirect('utilisateurs')
                user.delete()
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de l'utilisateur : {str(e)}")
            return redirect('utilisateurs')

        # Activer/Désactiver un utilisateur
        elif action == 'toggle_active':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                user.is_active = not user.is_active
                user.save()
            except Exception as e:
                messages.error(request, f"Erreur lors du changement de statut : {str(e)}")
            return redirect('utilisateurs')

    # Statistiques
    total_users = Utilisateur.objects.count()
    role_counts = {
        'Employé': Utilisateur.objects.filter(role__nom_role='Employé').count(),
        'RH': Utilisateur.objects.filter(role__nom_role='RH').count(),
        'Utilisateur': Utilisateur.objects.filter(role__nom_role='Utilisateur').count(),
    }

    # Vérifier si un RH existe pour le template
    rh_exists = Utilisateur.objects.filter(role__nom_role='RH').exists()

    # Liste des utilisateurs
    users_data = []
    for utilisateur in Utilisateur.objects.all():
        users_data.append({
            'id': utilisateur.user.id,
            'photo': utilisateur.url_photo if utilisateur.url_photo else 'https://via.placeholder.com/50',
            'nom': utilisateur.user.username,
            'role': utilisateur.role.nom_role,
            'email': utilisateur.user.email,
            'statut': 'Actif' if utilisateur.user.is_active else 'Inactif',
        })

    return render(request, 'html_of_pages/dashboard/utilisateurs.html', {
        'active_page': 'utilisateurs',
        'total_users': total_users,
        'role_counts': role_counts,
        'users_data': users_data,
        'roles': Role.objects.all(),
        'rh_exists': rh_exists,
    })

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
            unregister_training_id = request.POST.get('unregister_training_id')
            if training_id:
                training = Training.objects.get(id=training_id)
                TrainingRegistration.objects.create(employee=employee, training=training)
            elif unregister_training_id:
                registration = TrainingRegistration.objects.get(employee=employee, training_id=unregister_training_id)
                registration.delete()
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
@rh_required
def rh_trainings(request):
    if request.user.utilisateur.role.nom_role != 'RH':
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    trainings = Training.objects.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            try:
                Training.objects.create(
                    title=title,
                    description=description,
                    start_date=start_date,
                    end_date=end_date
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de la formation : {str(e)}")
            return redirect('rh_trainings')

        elif action == 'edit':
            training_id = request.POST.get('training_id')
            title = request.POST.get('title')
            description = request.POST.get('description')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            try:
                training = Training.objects.get(id=training_id)
                training.title = title
                training.description = description
                training.start_date = start_date
                training.end_date = end_date
                training.save()
            except Training.DoesNotExist:
                messages.error(request, "La formation spécifiée n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de la formation : {str(e)}")
            return redirect('rh_trainings')

        elif action == 'delete':
            training_id = request.POST.get('training_id')
            try:
                training = Training.objects.get(id=training_id)
                training.delete()
            except Training.DoesNotExist:
                messages.error(request, "La formation spécifiée n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de la formation : {str(e)}")
            return redirect('rh_trainings')

    return render(request, 'html_of_pages/dashboard/rh_trainings.html', {
        'active_page': 'rh_trainings',
        'trainings': trainings,
    })

# Se déconnecter
def logout_view(request):
    response = redirect('login')
    # Vérifier si le cookie "remember_me" existe et est à "true"
    remember_me = request.COOKIES.get('remember_me', 'false') == 'true'
    if not remember_me:
        # Si "Se souvenir de moi" n'était pas coché, supprimer les cookies
        response.delete_cookie('username')
        response.delete_cookie('password')
        response.delete_cookie('remember_me')
    # Déconnecter l'utilisateur
    logout(request)
    return response