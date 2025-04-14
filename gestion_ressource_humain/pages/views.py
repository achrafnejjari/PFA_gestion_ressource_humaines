from django.shortcuts import render

def index(request):
    return render(request, 'html_of_pages/index.html') 

def login(request):
    return render(request, 'html_of_pages/login.html')

def about(request):
    return render(request, 'html_of_pages/about.html')