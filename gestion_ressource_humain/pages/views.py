from django.shortcuts import render
from .models import Employee

def index(request):
    x = {'name': 'ahmed', 'age': 18}
    return render(request, 'html_of_pages/index.html', {'x': x})  # Make sure 'x' is passed as a dictionary
    

def list_employees(request):
    employees = Employee.objects.all() # Récupérer tous les employés
    return render(request, 'html_of_pages/employees.html', {'employees': employees}) # Passer les données au template