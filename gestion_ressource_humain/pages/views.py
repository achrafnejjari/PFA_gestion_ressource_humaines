from django.shortcuts import render , redirect , get_object_or_404
from django.contrib import messages #pour page contact (email)
from .models import Contact #pour page contact (email)

def index(request):
    return render(request, 'html_of_pages/index.html', {'active_page': 'index'}) 

def login(request):
    return render(request, 'html_of_pages/login.html', {'active_page': 'login'})

def about(request):
    return render(request, 'html_of_pages/about.html', {'active_page': 'about'})

def navbar(request):
    return render(request, 'html_of_pages/navbar.html', {'active_page': 'navbar'})

def signup(request):
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

def about(request):
    return render(request, 'html_of_pages/about.html', {'active_page': 'about'})

def joboffer(request):
    return render(request, 'html_of_pages/joboffer.html', {'active_page': 'joboffer'})

def sidebar(request):
    return render(request, 'html_of_pages/dashboard/sidebar.html', {'active_page': 'sidebar'})

def dashboard(request):
    return render(request, 'html_of_pages/dashboard/dashboard.html', {'active_page': 'dashboard'})

def departments(request):
    return render(request, 'html_of_pages/dashboard/departments.html', {'active_page': 'departments'})

def employees(request):
    return render(request, 'html_of_pages/dashboard/employees.html', {'active_page': 'employees'})

def contracts(request):
    return render(request, 'html_of_pages/dashboard/contracts.html', {'active_page': 'contracts'})

def performance(request):
    return render(request, 'html_of_pages/dashboard/performance.html', {'active_page': 'performance'})

def joboffer_dashboard(request):
    return render(request, 'html_of_pages/dashboard/joboffer_dashboard.html', {'active_page': 'joboffer_dashboard'})

def candidates(request):
    return render(request, 'html_of_pages/dashboard/candidates.html', {'active_page': 'candidates'})

def profile(request):
    return render(request, 'html_of_pages/dashboard/profile.html', {'active_page': 'profile'})

def settings(request):
    return render(request, 'html_of_pages/dashboard/settings.html', {'active_page': 'settings'})


def utulisateurs(request):
    return render(request, 'html_of_pages/dashboard/utulisateurs.html', {'active_page': 'utulisateurs'})

