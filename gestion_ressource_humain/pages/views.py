from django.shortcuts import render

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
    return render(request, 'html_of_pages/contact.html', {'active_page': 'contact'})

def services(request):
    return render(request, 'html_of_pages/services.html', {'active_page': 'services'})

def about(request):
    return render(request, 'html_of_pages/about.html', {'active_page': 'about'})

def joboffer(request):
    return render(request, 'html_of_pages/joboffer.html', {'active_page': 'joboffer'})



