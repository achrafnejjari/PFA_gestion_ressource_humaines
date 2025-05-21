# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages # departments , ..
# from django.core.files.storage import FileSystemStorage
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseForbidden
# from .models import Utilisateur, Role, Employe, Performance, Departement, Contrat, Conge, EmployeConge, Training, TrainingRegistration, Contact
# from datetime import date , datetime , timedelta
# from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
# from django.contrib.auth.forms import SetPasswordForm
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.urls import reverse_lazy
# from django.conf import settings

# from django.db.models import Count , Q , Avg #departments

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Utilisateur, Role, Employe, Performance, Departement, Contrat, Conge, EmployeConge, Training, TrainingRegistration, Contact, OffreEmploi, Candidat, Candidature
from datetime import date, datetime, timedelta
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Count, Q, Avg


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
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Sauvegarder le message dans la base de données
        Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        messages.success(request, "Votre message a été enregistré avec succès.")
        return redirect('contact')

    return render(request, 'html_of_pages/contact.html', {'active_page': 'contact'})

@login_required
@rh_required
def contact_messages(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        if message_id:
            message = get_object_or_404(Contact, id=message_id)
            message.delete()
            messages.success(request, "Le message a été supprimé avec succès.")
            return redirect('contact_messages')

    messages_list = Contact.objects.all()
    return render(request, 'html_of_pages/dashboard/contact_messages.html', {
        'messages_list': messages_list,
        'active_page': 'contact_messages'
    })

def services(request):
    return render(request, 'html_of_pages/services.html', {'active_page': 'services'})

def joboffer(request):
    # Récupérer les offres ouvertes (statut 'OUVERTE' et non expirées)
    today = date.today()
    job_offers = OffreEmploi.objects.filter(statut='OUVERTE', date_expiration__gte=today)

    # Pagination
    paginator = Paginator(job_offers, 6)  # Afficher 6 offres par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Déterminer si l'utilisateur peut postuler (authentifié, pas un employé, pas RH)
    can_apply = False
    if request.user.is_authenticated:
        is_employee = Employe.objects.filter(utilisateur__user=request.user).exists()
        is_rh = request.user.utilisateur.role.nom_role == 'RH'
        can_apply = not is_employee and not is_rh

    # Récupérer les offres auxquelles l'utilisateur a déjà postulé (basé sur l'email)
    applied_offers = set()
    if request.user.is_authenticated:
        user_email = request.user.email.lower()  # Normaliser l'email
        print(f"Utilisateur authentifié : {user_email}")
        applied_candidatures = Candidature.objects.filter(candidat__email__iexact=user_email).select_related('offre_emploi')
        applied_offers = {candidature.offre_emploi.id for candidature in applied_candidatures}
        print(f"Offres déjà postulées : {applied_offers}")

    # Vérifier si l'utilisateur a une candidature en attente
    has_pending_application = False
    if request.user.is_authenticated:
        user_email = request.user.email.lower()  # Normaliser l'email
        has_pending_application = Candidature.objects.filter(
            candidat__email__iexact=user_email,
            statut='EN_ATTENTE'
        ).exists()
        print(f"Candidature en attente : {has_pending_application}")

    if request.method == 'POST':
        if 'apply' in request.POST:
            if not can_apply:
                messages.error(request, "Les employés et le personnel RH ne peuvent pas postuler à des offres d'emploi.")
                return redirect('joboffer')

            if has_pending_application:
                messages.error(request, "Vous avez déjà une candidature en attente. Veuillez attendre la réponse avant de postuler à une autre offre.")
                return redirect('joboffer')

            offer_id = request.POST.get('offer_id')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            email = request.POST.get('email').lower()  # Normaliser l'email
            telephone = request.POST.get('telephone')
            cv = request.FILES.get('cv')

            # Vérifier que l'email correspond à celui de l'utilisateur connecté
            if email != request.user.email.lower():
                messages.error(request, "L'email fourni doit correspondre à votre email de connexion.")
                return redirect('joboffer')

            if not all([nom, prenom, email, telephone, cv]):
                messages.error(request, "Tous les champs sont requis.")
                return redirect('joboffer')

            if not cv.name.endswith('.pdf'):
                messages.error(request, "Le CV doit être au format PDF.")
                return redirect('joboffer')

            try:
                print(f"Tentative de création de candidature pour offre {offer_id} avec email {email}")
                candidat, created = Candidat.objects.get_or_create(
                    email=email,
                    defaults={
                        'nom': nom,
                        'prenom': prenom,
                        'telephone': telephone,
                        'cv': cv
                    }
                )
                if not created:
                    candidat.nom = nom
                    candidat.prenom = prenom
                    candidat.telephone = telephone
                    if cv:
                        candidat.cv = cv
                    candidat.save()
                    print(f"Candidat existant mis à jour : {candidat.email}")

                offer = get_object_or_404(OffreEmploi, id=offer_id)
                print(f"Offre récupérée : {offer.titre}")

                # Vérification explicite des candidatures existantes
                if Candidature.objects.filter(candidat=candidat, offre_emploi=offer).exists():
                    messages.error(request, "Vous avez déjà postulé pour cette offre.")
                    return redirect('joboffer')

                # Création de la candidature
                candidature = Candidature.objects.create(candidat=candidat, offre_emploi=offer, statut='EN_ATTENTE')
                print(f"Candidature créée avec succès : ID {candidature.id}")
                messages.success(request, "Votre candidature a été soumise avec succès.")

            except Exception as e:
                print(f"Erreur lors de la soumission : {str(e)}")
                messages.error(request, f"Erreur lors de la soumission de votre candidature : {str(e)}")
            return redirect('joboffer')

        elif 'cancel' in request.POST:
            offer_id = request.POST.get('offer_id')
            try:
                offer = get_object_or_404(OffreEmploi, id=offer_id)
                user_email = request.user.email.lower()  # Normaliser l'email
                candidature = Candidature.objects.get(candidat__email__iexact=user_email, offre_emploi=offer)
                candidature.delete()
                print(f"Candidature annulée pour l'offre {offer_id}")
                messages.success(request, "Votre candidature a été annulée avec succès.")
            except Candidature.DoesNotExist:
                messages.error(request, "Aucune candidature trouvée pour cette offre.")
            except Exception as e:
                print(f"Erreur lors de l'annulation : {str(e)}")
                messages.error(request, f"Erreur lors de l'annulation de votre candidature : {str(e)}")
            return redirect('joboffer')

    return render(request, 'html_of_pages/joboffer.html', {
        'active_page': 'joboffer',
        'page_obj': page_obj,
        'can_apply': can_apply,
        'applied_offers': applied_offers,
        'has_pending_application': has_pending_application
    })


# Dashboard
def sidebar(request):
    return render(request, 'html_of_pages/dashboard/sidebar.html', {'active_page': 'sidebar'})

# Accés aux pages dashboard
from datetime import date, timedelta

########################### DASHBOARD #################################

@login_required
def dashboard(request):
    role = request.user.utilisateur.role.nom_role

    if role == 'RH':
        # Statistiques globales
        total_employes = Employe.objects.count()
        total_departements = Departement.objects.count()
        total_candidatures = Contact.objects.count()
        
        # Ancienneté moyenne
        today = date.today()
        employes = Employe.objects.all()
        total_years = 0
        for emp in employes:
            years = today.year - emp.date_embauche.year
            if today.month < emp.date_embauche.month or (today.month == emp.date_embauche.month and today.day < emp.date_embauche.day):
                years -= 1
            total_years += years
        anciennete_moyenne = round(total_years / total_employes) if total_employes > 0 else 0

        # Nombre d'employés par type de contrat
        types_contrat = [
            {'type': 'CDI', 'count': Employe.objects.filter(contrat__type='CDI').count()},
            {'type': 'CDD', 'count': Employe.objects.filter(contrat__type='CDD').count()},
            {'type': 'Stage', 'count': Employe.objects.filter(contrat__type='STG').count()},
            {'type': 'Freelance', 'count': Employe.objects.filter(contrat__type='FRE').count()},
        ]

        # Proportion d'employés par département (en pourcentage)
        all_departements = Departement.objects.all().order_by('nom')
        print("Tous les départements :", list(all_departements.values('nom')))
        
        employe_counts = (
            Employe.objects.values('departement__nom')
            .annotate(count=Count('id'))
            .order_by('departement__nom')
        )
        print("Comptes bruts par département :", list(employe_counts))
        
        # Créer un dictionnaire des comptes
        count_dict = {
            item['departement__nom']: item['count']
            for item in employe_counts
            if item['departement__nom']  # Exclure les départements null
        }
        print("Dictionnaire des comptes :", count_dict)
        
        # Vérifier les employés sans département
        null_dept_count = Employe.objects.filter(departement__isnull=True).count()
        print("Employés sans département :", null_dept_count)
        
        # Calculer la somme totale des employés
        total_employes_count = sum(count_dict.values()) if count_dict else 0
        print("Total des employés comptés (excluant null) :", total_employes_count)
        print("Total des employés dans Employe.objects.count() :", total_employes)
        
        scores_par_departement = []
        for dept in all_departements:
            count = count_dict.get(dept.nom, 0)
            print(f"Compte pour {dept.nom} : {count}")
            percentage = round((count / total_employes_count * 100) if total_employes_count > 0 else 0.0, 2)
            scores_par_departement.append({
                'departement': dept.nom,
                'avg_score': percentage,
                'has_evaluations': count > 0,
                'count': count
            })
        print("Pourcentages par département :", scores_par_departement)
        print("Comptes dans scores_par_departement :", [item['count'] for item in scores_par_departement])

        # Liste des employés
        employees_data = []
        for employee in employes:
            # Calcul manuel de l'ancienneté
            years = today.year - employee.date_embauche.year
            months = today.month - employee.date_embauche.month
            if today.month < employee.date_embauche.month or (today.month == employee.date_embauche.month and today.day < employee.date_embauche.day):
                years -= 1
                months += 12
            if today.day < employee.date_embauche.day and today.month == employee.date_embauche.month:
                months -= 1
            if years > 0:
                anciennete = f"{years} an{'s' if years > 1 else ''}, {months} mois"
            elif months > 0:
                anciennete = f"{months} mois"
            else:
                anciennete = "Moins d'un mois"

            # Calcul de la moyenne des performances
            avg_performance = Performance.objects.filter(employe=employee).aggregate(Avg('score'))['score__avg']
            performance_score = f"{avg_performance:.2f}%" if avg_performance is not None else "N/A"

            employees_data.append({
                'nom': employee.nom,
                'prenom': employee.prenom,
                'email': employee.email,
                'telephone': employee.telephone,
                'salaire': f"{employee.salaire_actuel}€",
                'departement': employee.departement.nom if employee.departement else "Non spécifié",
                'anciennete': anciennete,
                'performance': performance_score,
                'date_embauche': employee.date_embauche.strftime('%d/%m/%Y'),
                'date_fin': employee.date_fin.strftime('%d/%m/%Y') if employee.date_fin else "-",
                'statut': employee.contrat.type if employee.contrat else "N/A",
            })

        return render(request, 'html_of_pages/dashboard/dashboard.html', {
            'active_page': 'dashboard',
            'employees_data': employees_data,
            'total_employes': total_employes,
            'total_departements': total_departements,
            'total_candidatures': total_candidatures,
            'anciennete_moyenne': anciennete_moyenne,
            'types_contrat': types_contrat,
            'scores_par_departement': scores_par_departement,
        })

    elif role == 'Employé':
        try:
            utilisateur = request.user.utilisateur
            employee = Employe.objects.get(utilisateur=utilisateur)
            today = date.today()
            years_of_service = today.year - employee.date_embauche.year
            if today.month < employee.date_embauche.month or (today.month == employee.date_embauche.month and today.day < employee.date_embauche.day):
                years_of_service -= 1

            performance = Performance.objects.filter(employe=employee).order_by('-date_evaluation').first()
            recent_performances = Performance.objects.filter(employe=employee).order_by('-date_evaluation')[:3]

            annual_leave_days = employee.contrat.leave_entitlement if employee.contrat and employee.contrat.leave_entitlement else 25
            employee_conges = EmployeConge.objects.filter(employe=employee)
            taken_days = 0
            for emp_conge in employee_conges:
                if emp_conge.conge.statut == 'APPROUVE':
                    delta = (emp_conge.conge.date_fin - emp_conge.conge.date_debut).days + 1
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
                'annual_leave_days': 25,
            })

    else:
        return render(request, 'html_of_pages/dashboard/user_dashboard.html', {
            'active_page': 'dashboard',
        })
#########################################################################

########################## DEPARTEMENTS ################################33

# page  departments  !

@login_required
@rh_required
def departments(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            nom = request.POST.get('nom')
            description = request.POST.get('description', '')
            if nom:
                Departement.objects.create(nom=nom, description=description)
            else:
                messages.error(request, 'Le nom du département est requis.')
        elif action == 'edit':
            department_id = request.POST.get('department_id')
            nom = request.POST.get('nom')
            description = request.POST.get('description', '')
            try:
                department = Departement.objects.get(id=department_id)
                if nom:
                    department.nom = nom
                    department.description = description
                    department.save()
                else:
                    messages.error(request, 'Le nom du département est requis.')
            except Departement.DoesNotExist:
                messages.error(request, 'Le département spécifié n’existe pas.')
        elif action == 'delete':
            department_id = request.POST.get('department_id')
            try:
                department = Departement.objects.get(id=department_id)
                department.delete()
            except Departement.DoesNotExist:
                messages.error(request, 'Le département spécifié n’existe pas.')
        return redirect('departments')

    departments = Departement.objects.all()
    total_departments = departments.count()
    department_employee_counts = Employe.objects.values('departement__nom').annotate(
        employee_count=Count('id')
    ).order_by('-employee_count')[:4]
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(nom__icontains=search_query)

    context = {
        'active_page': 'departments',
        'departments': departments,
        'total_departments': total_departments,
        'department_employee_counts': department_employee_counts,
        'search_query': search_query,
    }
    return render(request, 'html_of_pages/dashboard/departments.html', context)



#########################################################################

########################### employees ##############################
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
                    leave_entitlement=25  # Valeur par défaut, comme dans contracts
                )

                # Récupérer l'utilisateur à lier (si sélectionné)
                utilisateur = None
                if utilisateur_id:
                    utilisateur = Utilisateur.objects.get(id=utilisateur_id)
                    # S'assurer que l'utilisateur n'est pas déjà lié à un autre employé
                    if Employe.objects.filter(utilisateur=utilisateur).exists():
                        messages.error(request, "Cet utilisateur est déjà lié à un autre employé.")
                        contrat.delete()  # Nettoyer le contrat créé
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
                    salaire_actuel=salaire_actuel if salaire_actuel else None,
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

                # Vérifier si cet employé est lié à l'utilisateur RH
                if employee.utilisateur == request.user.utilisateur:
                    messages.error(request, "Vous ne pouvez pas modifier votre propre profil d'employé ici.")
                    return redirect('employees')

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
                # préserver l'utilisateur lié à l'employé
                elif not utilisateur_id and employee.utilisateur:
                    pass

                # Mettre à jour l'employé
                employee.nom = nom
                employee.prenom = prenom
                employee.date_de_naissance = date_de_naissance
                employee.email = email
                employee.telephone = telephone
                employee.salaire_actuel = salaire_actuel if salaire_actuel else None
                employee.date_embauche = date_embauche
                employee.date_fin = date_fin if date_fin else None
                employee.departement = Departement.objects.get(id=departement_id)

                # Mettre à jour ou créer un contrat
                if employee.contrat:
                    employee.contrat.type = type_contrat
                    employee.contrat.save()
                else:
                    employee.contrat = Contrat.objects.create(
                        type=type_contrat,
                        leave_entitlement=25
                    )
                employee.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'employé : {str(e)}")
            return redirect('employees')

        # Supprimer un employé
        elif action == 'delete_employee':
            employee_id = request.POST.get('employee_id')
            try:
                employee = Employe.objects.get(id=employee_id)
                # Vérifier si cet employé est lié à l'utilisateur RH
                if employee.utilisateur == request.user.utilisateur:
                    messages.error(request, "Vous ne pouvez pas supprimer votre propre profil d'employé.")
                    return redirect('employees')
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
        if count > 0:
            departement_counts[departement.nom] = count

    # Liste des utilisateurs avec le rôle "Employé" disponibles
    available_employe_users = Utilisateur.objects.filter(
        role__nom_role='Employé'
    ).exclude(
        employe__isnull=False
    )

    # Liste des employés
    employees_data = []
    for employee in Employe.objects.all():
        # Vérifier si l'employé est lié à l'utilisateur RH
        is_rh_employee = employee.utilisateur == request.user.utilisateur
        employees_data.append({
            'id': employee.id,
            'nom': employee.nom,
            'prenom': employee.prenom,
            'utilisateur_id': employee.utilisateur.id if employee.utilisateur else None,
            'utilisateur_username': employee.utilisateur.user.username if employee.utilisateur else None,
            'date_de_naissance': employee.date_de_naissance.strftime('%d/%m/%Y'),
            'email': employee.email,
            'telephone': employee.telephone,
            'salaire': f"{employee.salaire_actuel}€" if employee.salaire_actuel else "Non spécifié",
            'departement': employee.departement.nom if employee.departement else "Non spécifié",
            'departement_id': employee.departement.id if employee.departement else None,
            'date_embauche': employee.date_embauche.strftime('%d/%m/%Y') if employee.date_embauche else "Non défini",
            'date_fin': employee.date_fin.strftime('%d/%m/%Y') if employee.date_fin else "-",
            'type_contrat': employee.contrat.type if employee.contrat else "N/A",
            'is_rh_employee': is_rh_employee,  # Ajout du flag pour indiquer si c'est l'employé RH
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
        'available_employe_users': available_employe_users,
    })


#########################################################################


########################### CONTRACTS #################################
@login_required
@rh_required
def contracts(request):
    today = datetime.today().date()
    thirty_days_later = today + timedelta(days=30)
    # Gestion des actions POST
    if request.method == 'POST':
        action = request.POST.get('action')

        # Modifier un contrat
        if action == 'edit':
            contrat_id = request.POST.get('contrat_id')
            leave_entitlement = request.POST.get('leave_entitlement', 25)
            type_contrat = request.POST.get('type_contrat')
            date_embauche = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin', None)
            salaire_actuel = request.POST.get('salaire', None)

            try:
                contrat = Contrat.objects.get(contract_id=contrat_id)
                employe = Employe.objects.filter(contrat=contrat).first()
                if not employe:
                    messages.error(request, "Ce contrat n'est associé à aucun employé.")
                else:
                    # Mettre à jour Contrat
                    contrat.leave_entitlement = leave_entitlement
                    contrat.type = type_contrat
                    contrat.save()
                    # Mettre à jour Employe
                    if date_embauche:
                        employe.date_embauche = date_embauche
                    if date_fin:
                        employe.date_fin = date_fin
                    else:
                        employe.date_fin = None
                    if salaire_actuel:
                        employe.salaire_actuel = salaire_actuel
                    else:
                        employe.salaire_actuel = None
                    employe.save()
            except Contrat.DoesNotExist:
                messages.error(request, "Le contrat spécifié n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification du contrat : {str(e)}")

        # Supprimer un contrat
        elif action == 'delete':
            contrat_id = request.POST.get('contrat_id')
            try:
                contrat = Contrat.objects.get(contract_id=contrat_id)
                employe = Employe.objects.filter(contrat=contrat).first()
                if employe:
                    employe.contrat = None
                    employe.save()
                contrat.delete()
            except Contrat.DoesNotExist:
                messages.error(request, "Le contrat spécifié n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression du contrat : {str(e)}")

        # Ajouter un contrat
        elif action == 'add':
            employe_id = request.POST.get('employe_id')
            leave_entitlement = request.POST.get('leave_entitlement', 25)
            type_contrat = request.POST.get('type_contrat')
            date_embauche = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin', None)
            salaire_actuel = request.POST.get('salaire', None)

            try:
                employe = Employe.objects.get(id=employe_id)
                if employe.contrat:
                    messages.error(request, "Cet employé a déjà un contrat.")
                else:
                    contrat = Contrat.objects.create(
                        type=type_contrat,
                        leave_entitlement=leave_entitlement
                    )
                    employe.contrat = contrat
                    if date_embauche:
                        employe.date_embauche = date_embauche
                    if date_fin:
                        employe.date_fin = date_fin
                    if salaire_actuel:
                        employe.salaire_actuel = salaire_actuel
                    employe.save()
            except Employe.DoesNotExist:
                messages.error(request, "L'employé spécifié n'existe pas.")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout du contrat : {str(e)}")

        return redirect('contracts')

    # Gestion de la requête GET
    employes_avec_contrat = Employe.objects.filter(contrat__isnull=False)
    contrats = Contrat.objects.filter(id__in=employes_avec_contrat.values('contrat'))
    today = date.today()
    threshold_date = today + timedelta(days=30)

    # Calcul des statistiques
    total_contrats = Contrat.objects.count()
    actifs = Employe.objects.filter(
        Q(contrat__isnull=False) &
        (Q(date_fin__isnull=True) | Q(date_fin__gt=thirty_days_later))
    ).count()
    expires = Employe.objects.filter(
        contrat__isnull=False,
        date_fin__lte=today
    ).count()
    a_expirer = Employe.objects.filter(
        contrat__isnull=False,
        date_fin__gt=today,
        date_fin__lte=thirty_days_later
    ).count()
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        employes_avec_contrat = employes_avec_contrat.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query)
        )
        contrats = Contrat.objects.filter(id__in=employes_avec_contrat.values('contrat'))

    # Liste des employés sans contrat pour l'ajout
    employes_sans_contrat = Employe.objects.filter(contrat__isnull=True)

    # Préparer les données pour le tableau
    contrats_data = []
    for contrat in contrats:
        employe = Employe.objects.filter(contrat=contrat).first()
        statut = "Actif" if not employe.date_fin or employe.date_fin > today else "Expiré"
        if employe.date_fin and today < employe.date_fin <= threshold_date:
            statut = "À expirer"
        contrats_data.append({
            'contract_id': contrat.contract_id,
            'employe_id': employe.id,
            'employe_nom': f"{employe.nom} {employe.prenom}",
            'type': contrat.type,
            'date_embauche': employe.date_embauche.strftime('%Y-%m-%d') if employe.date_embauche else 'Non défini',
            'date_fin': employe.date_fin.strftime('%Y-%m-%d') if employe.date_fin else '--',
            'salaire': str(employe.salaire_actuel) if employe.salaire_actuel else 'Non spécifié',
            'leave_entitlement': contrat.leave_entitlement,
            'statut': statut,
        })

    context = {
        'active_page': 'contracts',
        'contrats_data': contrats_data,
        'total_contrats': total_contrats,
        'actifs': actifs,
        'expires': expires,
        'a_expirer': a_expirer,
        'search_query': search_query,
        'type_choices': Contrat.TYPE_CHOICES,
        'employes_sans_contrat': employes_sans_contrat,
    }
    return render(request, 'html_of_pages/dashboard/contracts.html', context)

######################### PERFORMANCE #######################

@login_required
@rh_required
def performance(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        # Ajouter une évaluation
        if action == 'add_performance':
            employe_id = request.POST.get('employe_id')
            objectif = request.POST.get('objectif')
            score = request.POST.get('score')
            commentaire = request.POST.get('commentaire', '')
            debut_objectif = request.POST.get('debut_objectif')
            fin_objectif = request.POST.get('fin_objectif')

            try:
                employe = Employe.objects.get(id=employe_id)
                Performance.objects.create(
                    employe=employe,
                    objectif=objectif,
                    score=score,
                    commentaire=commentaire,
                    debut_objectif=debut_objectif,
                    fin_objectif=fin_objectif,
                    date_evaluation=date.today()
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'évaluation : {str(e)}")
            return redirect('performance')

        # Modifier une évaluation
        elif action == 'edit_performance':
            performance_id = request.POST.get('performance_id')
            employe_id = request.POST.get('employe_id')
            objectif = request.POST.get('objectif')
            score = request.POST.get('score')
            commentaire = request.POST.get('commentaire', '')
            debut_objectif = request.POST.get('debut_objectif')
            fin_objectif = request.POST.get('fin_objectif')

            try:
                performance = Performance.objects.get(id=performance_id)
                performance.employe = Employe.objects.get(id=employe_id)
                performance.objectif = objectif
                performance.score = score
                performance.commentaire = commentaire
                performance.debut_objectif = debut_objectif
                performance.fin_objectif = fin_objectif
                performance.date_evaluation = date.today()
                performance.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'évaluation : {str(e)}")
            return redirect('performance')

        # Supprimer une évaluation
        elif action == 'delete_performance':
            performance_id = request.POST.get('performance_id')
            try:
                performance = Performance.objects.get(id=performance_id)
                performance.delete()
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de l'évaluation : {str(e)}")
            return redirect('performance')

    # Calcul des statistiques
    performances = Performance.objects.all()
    moyenne_score = performances.aggregate(Avg('score'))['score__avg'] or 0
    moyenne_score = round(moyenne_score, 2)
    excellent_count = performances.filter(score__gte=90).count()
    moyen_count = performances.filter(score__gte=70, score__lt=90).count()
    faible_count = performances.filter(score__lt=70).count()

    # Données pour le tableau
    performances_data = []
    for perf in performances:
        performances_data.append({
            'id': perf.id,
            'employe_id': perf.employe.id,
            'employe_nom': f"{perf.employe.nom} {perf.employe.prenom}",
            'departement': perf.employe.departement.nom if perf.employe.departement else "Non spécifié",
            'objectif': perf.objectif,
            'score': perf.score,
            'commentaire': perf.commentaire,
            'debut_objectif': perf.debut_objectif.strftime('%Y-%m-%d'),
            'fin_objectif': perf.fin_objectif.strftime('%Y-%m-%d'),
            'periode_objectif': perf.periode_objectif(),
        })

    # Liste des employés pour le formulaire
    employes = Employe.objects.all().select_related('departement')

    return render(request, 'html_of_pages/dashboard/performance.html', {
        'active_page': 'performance',
        'moyenne_score': moyenne_score,
        'excellent_count': excellent_count,
        'moyen_count': moyen_count,
        'faible_count': faible_count,
        'performances': performances_data,
        'employes': employes,
    })

#########################################################################
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
        employee_conges = EmployeConge.objects.filter(employe=employee).select_related('conge').order_by('-conge__created_at')

        # Calculate remaining days for context
        annual_leave_days = employee.contrat.leave_entitlement if employee.contrat and employee.contrat.leave_entitlement else 25
        taken_days = sum((ec.conge.date_fin - ec.conge.date_debut).days + 1 for ec in employee_conges if ec.conge.statut == 'APPROUVE')
        remaining_days = annual_leave_days - taken_days

        # Calculate pending days for display (informational only)
        pending_days = sum((ec.conge.date_fin - ec.conge.date_debut).days + 1 for ec in employee_conges if ec.conge.statut == 'EN_ATTENTE')

        # Calculate tomorrow's date dynamically
        tomorrow_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

        # Bulk update expired leaves
        current_date = datetime.now().date()
        Conge.objects.filter(
            employeconge__employe=employee,
            date_fin__lt=current_date,
            statut__in=['EN_ATTENTE', 'APPROUVE']
        ).update(statut='EXPIRE')

        # Check for existing pending requests
        has_pending_request = employee_conges.filter(conge__statut='EN_ATTENTE').exists()

        if request.method == 'POST' and not has_pending_request:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason', 'Congé annuel')

            # Validate dates
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Erreur : Les dates fournies ne sont pas valides.")
                return redirect('leave_requests')

            if end < start:
                messages.error(request, "Erreur : La date de fin ne peut pas être antérieure à la date de début.")
                return redirect('leave_requests')

            # Calculate requested days (inclusive of start and end dates)
            requested_days = (end - start).days + 1

            # Server-side validation for remaining days (as a fallback)
            if requested_days > remaining_days:
                messages.error(request, f"Erreur : Vous avez demandé {requested_days} jours, mais il ne vous reste que {remaining_days} jours de congé.")
                return redirect('leave_requests')

            # Validate dates against tomorrow
            tomorrow = datetime.now().date() + timedelta(days=1)
            if start < tomorrow or end < tomorrow:
                messages.error(request, f"Erreur : Les dates doivent être à partir de demain ({tomorrow.strftime('%d/%m/%Y')}).")
                return redirect('leave_requests')

            # Create the leave request
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
        elif request.method == 'POST' and has_pending_request:
            messages.error(request, "Vous avez déjà une demande de congé en attente. Veuillez attendre la réponse de RH avant de soumettre une nouvelle demande.")
            return redirect('leave_requests')

        return render(request, 'html_of_pages/dashboard/leave_requests.html', {
            'active_page': 'leave_requests',
            'employee_conges': employee_conges,
            'employee': employee,
            'remaining_days': remaining_days,
            'taken_days': taken_days,
            'pending_days': pending_days,
            'has_pending_request': has_pending_request,
            'tomorrow_date': tomorrow_date,
        })
    except Employe.DoesNotExist:
        tomorrow_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')
        return render(request, 'html_of_pages/dashboard/leave_requests.html', {
            'active_page': 'leave_requests',
            'employee_conges': [],
            'remaining_days': 0,
            'taken_days': 0,
            'pending_days': 0,
            'has_pending_request': False,
            'tomorrow_date': tomorrow_date,
        })
    

@login_required
@rh_required
def joboffer_dashboard(request):
    today = date.today()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            titre = request.POST.get('titre')
            description = request.POST.get('description', '')
            date_expiration = request.POST.get('date_expiration')
            departement_id = request.POST.get('departement')
            competences_requises = request.POST.get('competences_requises', '')
            salaire = request.POST.get('salaire', '')

            if not all([titre, date_expiration, departement_id]):
                messages.error(request, "Tous les champs requis doivent être remplis.")
                return redirect('joboffer_dashboard')

            try:
                departement = Departement.objects.get(id=departement_id)
                OffreEmploi.objects.create(
                    titre=titre,
                    description=description,
                    date_publication=today,
                    date_expiration=date_expiration,
                    competences_requises=competences_requises,
                    salaire=salaire,
                    departement=departement,
                    statut='OUVERTE'
                )

            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout de l'offre : {str(e)}")
            return redirect('joboffer_dashboard')

        elif action == 'edit':
            offer_id = request.POST.get('offer_id')
            titre = request.POST.get('titre')
            description = request.POST.get('description', '')
            date_expiration = request.POST.get('date_expiration')
            departement_id = request.POST.get('departement')
            competences_requises = request.POST.get('competences_requises', '')
            salaire = request.POST.get('salaire', '')
            statut = request.POST.get('statut')

            if not all([offer_id, titre, date_expiration, departement_id, statut]):
                messages.error(request, "Tous les champs requis doivent être remplis.")
                return redirect('joboffer_dashboard')

            try:
                offer = get_object_or_404(OffreEmploi, id=offer_id)
                departement = Departement.objects.get(id=departement_id)
                offer.titre = titre
                offer.description = description
                offer.date_expiration = date_expiration
                offer.departement = departement
                offer.competences_requises = competences_requises
                offer.salaire = salaire
                offer.statut = statut
                offer.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification de l'offre : {str(e)}")
            return redirect('joboffer_dashboard')

        elif action == 'delete':
            offer_id = request.POST.get('offer_id')
            try:
                offer = get_object_or_404(OffreEmploi, id=offer_id)
                offer.delete()
            except Exception as e:
                messages.error(request, f"Erreur lors de la suppression de l'offre : {str(e)}")
            return redirect('joboffer_dashboard')

    # Fetch all job offers with applicant counts
    job_offers = OffreEmploi.objects.all()
    open_count = job_offers.filter(statut='OUVERTE', date_expiration__gte=today).count()
    closed_count = job_offers.filter(statut='FERMEE').count()
    expired_count = job_offers.filter(date_expiration__lt=today).count()

    # Prepare data with applicant counts
    job_offers_data = []
    for offer in job_offers:
        applicant_count = Candidature.objects.filter(offre_emploi=offer).count()
        job_offers_data.append({
            'offer': offer,
            'applicant_count': applicant_count
        })

    # Pagination
    paginator = Paginator(job_offers_data, 6)  # Show 6 offers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'html_of_pages/dashboard/joboffer_dashboard.html', {
        'active_page': 'joboffer_dashboard',
        'page_obj': page_obj,
        'open_count': open_count,
        'closed_count': closed_count,
        'expired_count': expired_count,
        'departements': Departement.objects.all(),
    })

@login_required
def user_joboffers(request):
    if request.user.utilisateur.role.nom_role not in ['Utilisateur', 'Employé']:
        return HttpResponseForbidden("Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
    
    try:
        user_email = request.user.email
        # Fetch candidatures for the current user
        candidatures = Candidature.objects.filter(candidat__email=user_email).select_related('offre_emploi')
        
        # Extract applied job offers
        job_offers = []
        for candidature in candidatures:
            offer = candidature.offre_emploi
            job_offers.append({
                'titre': offer.titre,
                'departement': offer.departement.nom,
                'date_publication': offer.date_publication.strftime('%d/%m/%Y'),
                'statut': candidature.statut,
                'date_submission': candidature.date_submission.strftime('%d/%m/%Y')
            })

        return render(request, 'html_of_pages/dashboard/user_joboffers.html', {
            'active_page': 'user_joboffers',
            'job_offers': job_offers
        })
    except Exception as e:
        messages.error(request, f"Une erreur s'est produite : {str(e)}")
        return render(request, 'html_of_pages/dashboard/user_joboffers.html', {
            'active_page': 'user_joboffers',
            'job_offers': []
        })

@login_required
@rh_required
def candidates(request):
    today = date.today()
    if request.method == 'POST':
        action = request.POST.get('action')
        candidature_id = request.POST.get('candidature_id')
        if action in ['approve', 'reject'] and candidature_id:
            try:
                candidature = get_object_or_404(Candidature, id=candidature_id)
                candidature.statut = 'ACCEPTEE' if action == 'approve' else 'REJETEE'
                candidature.save()
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour de la candidature : {str(e)}")
            return redirect('candidates')

    # Fetch all candidatures with related data
    candidatures = Candidature.objects.select_related('candidat', 'offre_emploi').all()
    candidates_data = []
    for candidature in candidatures:
        # Construct the full CV URL
        cv_link = None
        if candidature.candidat.cv:
            cv_link = request.build_absolute_uri(candidature.candidat.cv.url)
        candidates_data.append({
            'id': candidature.id,
            'nom': candidature.candidat.nom,
            'prenom': candidature.candidat.prenom,
            'email': candidature.candidat.email,
            'telephone': candidature.candidat.telephone,
            'offre_titre': candidature.offre_emploi.titre,
            'date_submission': candidature.date_submission.strftime('%d/%m/%Y'),
            'statut': candidature.statut,
            'cv_link': cv_link,
        })

    # Pagination
    paginator = Paginator(candidates_data, 10)  # Show 10 candidates per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'html_of_pages/dashboard/candidates.html', {
        'active_page': 'candidates',
        'page_obj': page_obj,
    })


############################################################
############################  PROFIL ###############################

@login_required
def profile(request):
    utilisateur = request.user.utilisateur
    today = date.today()
    
    # Log pour déboguer
    print(f"Request.user: {request.user}, Authentifié: {request.user.is_authenticated}")
    print(f"Utilisateur: {utilisateur}, User: {utilisateur.user}, Rôle: {getattr(utilisateur.role, 'nom_role', 'Aucun')}")
    print(f"Username: {request.user.username}, Email: {request.user.email}, Téléphone: {getattr(utilisateur, 'telephone', 'N/A')}")

    # Vérifier si utilisateur.user existe
    if not utilisateur.user:
        print("Erreur: utilisateur.user est None")
        profile_data = {
            'username': "Inconnu",
            'role': "N/A",
            'nom_complet': "Inconnu",
            'email': "N/A",
        }
        return render(request, 'html_of_pages/dashboard/profile.html', {
            'active_page': 'profile',
            'utilisateur': utilisateur,
            'profile_data': profile_data,
        })

    # Récupérer le rôle
    role = getattr(utilisateur.role, 'nom_role', None)

    # Récupérer l'employé lié à l'utilisateur
    employe = None
    if role in ['Employé', 'RH']:
        try:
            employe = Employe.objects.get(utilisateur=utilisateur)
            print(f"Employé trouvé: {employe.nom} {employe.prenom}, Email: {employe.email}, Date embauche: {employe.date_embauche}")
        except Employe.DoesNotExist:
            print(f"Aucun Employé trouvé pour utilisateur: {request.user.username} (Email: {request.user.email})")
            employe = None

    # Traitement du formulaire de modification
    if request.method == 'POST':
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        photo = request.FILES.get('photo')

        # Mettre à jour Utilisateur
        if email:
            utilisateur.user.email = email
            utilisateur.user.save()
            print(f"Email mis à jour: {email}")
        if telephone and role in ['Employé', 'RH']:
            try:
                utilisateur.telephone = telephone
                utilisateur.save()
                print(f"Téléphone mis à jour: {telephone}")
            except AttributeError:
                print("Champ telephone non disponible dans Utilisateur; mise à jour ignorée")

        # Mettre à jour Employe si applicable
        if employe and role in ['Employé', 'RH']:
            if nom:
                employe.nom = nom
            if prenom:
                employe.prenom = prenom
            if email:
                employe.email = email
            if telephone:
                employe.telephone = telephone
            employe.save()
            print(f"Employé mis à jour: {nom} {prenom}, Email: {email}, Téléphone: {telephone}")

        # Gérer l'upload de photo
        if photo:
            fs = FileSystemStorage()
            filename = fs.save(f'photos/{photo.name}', photo)
            photo_url = fs.url(filename)
            utilisateur.url_photo = photo_url
            utilisateur.save()
            print(f"Photo uploadée: {photo_url}")

        return redirect('profile')

    # Données pour le template
    profile_data = {}
    if employe and role == 'Employé':
        # Calcul manuel de l'ancienneté
        years = today.year - employe.date_embauche.year
        months = today.month - employe.date_embauche.month
        if today.month < employe.date_embauche.month or (today.month == employe.date_embauche.month and today.day < employe.date_embauche.day):
            years -= 1
            months += 12
        if today.day < employe.date_embauche.day and today.month == employe.date_embauche.month:
            months -= 1
        if years > 0:
            anciennete = f"{years} an{'s' if years > 1 else ''}"
        elif months > 0:
            anciennete = f"{months} mois"
        else:
            anciennete = "Moins d'un mois"

        # Dernier score de performance
        dernier_performance = Performance.objects.filter(employe=employe).order_by('-date_evaluation').first()
        performance_score = f"{dernier_performance.score}%" if dernier_performance else "N/A"

        # Dernier congé
        dernier_conge = EmployeConge.objects.filter(employe=employe).order_by('-conge__date_debut').first()
        conge_statut = dernier_conge.conge.statut if dernier_conge else "Aucun"

        # Données pour Employé
        profile_data = {
            'username': request.user.username,
            'role': role,
            'nom_complet': f"{employe.nom} {employe.prenom}",
            'nom': employe.nom,
            'prenom': employe.prenom,
            'email': employe.email or request.user.email,
            'telephone': employe.telephone or getattr(utilisateur, 'telephone', "N/A"),
            'departement': employe.departement.nom if employe.departement else "Non spécifié",
            'anciennete': anciennete,
            'performance_score': performance_score,
            'type_contrat': employe.contrat.type if employe.contrat else "N/A",
            'date_embauche': employe.date_embauche.strftime('%d/%m/%Y') if employe.date_embauche else "N/A",
            'salaire_actuel': f"{employe.salaire_actuel:,} €".replace(",", " ") if employe.salaire_actuel else "N/A",
            'dernier_conge': conge_statut,
            'date_debut_contrat': employe.date_embauche.strftime('%d/%m/%Y') if employe.date_embauche else "N/A",
            'date_fin_contrat': employe.date_fin.strftime('%d/%m/%Y') if employe.date_fin else "Indéterminée",
        }
    elif role == 'RH':
        # Données limitées pour RH
        profile_data = {
            'username': request.user.username,
            'role': role,
            'nom_complet': employe.nom + ' ' + employe.prenom if employe else request.user.username,
            'nom': employe.nom if employe else request.user.username,
            'prenom': employe.prenom if employe else '',
            'email': employe.email if employe else request.user.email,
            'telephone': employe.telephone if employe else getattr(utilisateur, 'telephone', "0765437853"),
            'departement': employe.departement.nom if employe and employe.departement else "RH",
        }
    elif role == 'Utilisateur':
        # Données pour Utilisateur
        profile_data = {
            'username': request.user.username,
            'role': role,
            'nom_complet': request.user.username,
            'nom': request.user.username,
            'prenom': '',
            'email': request.user.email,
        }
    else:
        # Autres rôles ou pas de rôle
        profile_data = {
            'username': request.user.username,
            'role': role or "N/A",
            'nom_complet': request.user.username,
            'nom': request.user.username,
            'prenom': '',
            'email': request.user.email,
        }

    return render(request, 'html_of_pages/dashboard/profile.html', {
        'active_page': 'profile',
        'utilisateur': utilisateur,
        'profile_data': profile_data,
    })


#######################################################################################
@login_required
def settings(request):
    if request.method == 'POST':
        old_password = request.POST.get('old-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        # Validate old password
        if not request.user.check_password(old_password):
            messages.error(request, "L'ancien mot de passe est incorrect.")
            return redirect('settings')

        # Validate new password and confirmation
        if new_password != confirm_password:
            messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
            return redirect('settings')

        # Validate password strength (optional, customize as needed)
        if len(new_password) < 8:
            messages.error(request, "Le nouveau mot de passe doit contenir au moins 8 caractères.")
            return redirect('settings')

        # Update password and invalidate session
        request.user.set_password(new_password)
        request.user.save()
        logout(request)  # Invalidate session
        messages.success(request, "Votre mot de passe a été modifié. Veuillez vous reconnecter.")
        return redirect('login')

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
            if role_name == 'RH' and rh_count >= 2:
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