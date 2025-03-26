from django.contrib import admin
from .models import Role, Utilisateur, Departement, Contrat, Employe, Performance, Conge, EmployeConge, OffreEmploi, Candidat, Candidature

admin.site.register(Role)
admin.site.register(Utilisateur)
admin.site.register(Departement)
admin.site.register(Contrat)
admin.site.register(Employe)
admin.site.register(Performance)
admin.site.register(Conge)
admin.site.register(EmployeConge)
admin.site.register(OffreEmploi)
admin.site.register(Candidat)
admin.site.register(Candidature)