from django.shortcuts import render
from .models import Departement

def index(request):
    x = {'name': 'ahmed', 'age': 18}
    return render(request, 'html_of_pages/index.html', {'x': x})  # Make sure 'x' is passed as a dictionary
    

def list_employees(request):
    departements = Departement.objects.all() # Récupérer tous les employés
    return render(request, 'html_of_pages/employees.html', {'la_departement': departements}) # Passer les données au template