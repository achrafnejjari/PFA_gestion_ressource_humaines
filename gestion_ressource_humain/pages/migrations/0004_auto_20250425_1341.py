# Generated by Django 3.2.25 on 2025-04-25 13:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0003_auto_20250326_1209'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candidat',
            options={'verbose_name': 'Candidat', 'verbose_name_plural': 'Candidats'},
        ),
        migrations.AlterModelOptions(
            name='candidature',
            options={'verbose_name': 'Candidature', 'verbose_name_plural': 'Candidatures'},
        ),
        migrations.AlterModelOptions(
            name='conge',
            options={'verbose_name': 'Congé', 'verbose_name_plural': 'Congés'},
        ),
        migrations.AlterModelOptions(
            name='contrat',
            options={'verbose_name': 'Contrat', 'verbose_name_plural': 'Contrats'},
        ),
        migrations.AlterModelOptions(
            name='departement',
            options={'verbose_name': 'Département', 'verbose_name_plural': 'Départements'},
        ),
        migrations.AlterModelOptions(
            name='employe',
            options={'ordering': ['nom', 'prenom'], 'verbose_name': 'Employé', 'verbose_name_plural': 'Employés'},
        ),
        migrations.AlterModelOptions(
            name='employeconge',
            options={'verbose_name': 'Employé-Congé', 'verbose_name_plural': 'Employés-Congés'},
        ),
        migrations.AlterModelOptions(
            name='offreemploi',
            options={'verbose_name': "Offre d'emploi", 'verbose_name_plural': "Offres d'emploi"},
        ),
        migrations.AlterModelOptions(
            name='performance',
            options={'verbose_name': 'Performance', 'verbose_name_plural': 'Performances'},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Rôle', 'verbose_name_plural': 'Rôles'},
        ),
        migrations.AlterModelOptions(
            name='utilisateur',
            options={'verbose_name': 'Utilisateur', 'verbose_name_plural': 'Utilisateurs'},
        ),
        migrations.RemoveField(
            model_name='utilisateur',
            name='mot_de_passe',
        ),
        migrations.RemoveField(
            model_name='utilisateur',
            name='nom_utilisateur',
        ),
        migrations.AddField(
            model_name='employe',
            name='date_de_naissance',
            field=models.DateField(default=datetime.date(2000, 1, 1)),
        ),
        migrations.AddField(
            model_name='employe',
            name='date_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offreemploi',
            name='statut',
            field=models.CharField(choices=[('OUVERTE', 'Ouverte'), ('FERMEE', 'Fermée')], default='OUVERTE', max_length=50),
        ),
        migrations.AddField(
            model_name='performance',
            name='date_evaluation',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='performance',
            name='debut_objectif',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='performance',
            name='fin_objectif',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='url_photo',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='candidat',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to='cv/'),
        ),
        migrations.AlterField(
            model_name='candidat',
            name='email',
            field=models.EmailField(db_index=True, default='candidat@example.com', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='candidat',
            name='nom',
            field=models.CharField(default='Inconnu', max_length=255),
        ),
        migrations.AlterField(
            model_name='candidat',
            name='prenom',
            field=models.CharField(default='Inconnu', max_length=255),
        ),
        migrations.AlterField(
            model_name='candidat',
            name='telephone',
            field=models.CharField(default='0000000000', max_length=20),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='candidat',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.candidat'),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='offre_emploi',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.offreemploi'),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='statut',
            field=models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('ACCEPTEE', 'Acceptée'), ('REJETEE', 'Rejetée')], default='EN_ATTENTE', max_length=50),
        ),
        migrations.AlterField(
            model_name='conge',
            name='date_debut',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='conge',
            name='date_fin',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='conge',
            name='statut',
            field=models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('APPROUVE', 'Approuvé'), ('REFUSE', 'Refusé')], default='EN_ATTENTE', max_length=50),
        ),
        migrations.AlterField(
            model_name='conge',
            name='type',
            field=models.CharField(default='Congé annuel', max_length=50),
        ),
        migrations.AlterField(
            model_name='contrat',
            name='date_debut',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='contrat',
            name='date_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='contrat',
            name='salaire_initial',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='contrat',
            name='type',
            field=models.CharField(choices=[('CDI', 'Contrat à Durée Indéterminée'), ('CDD', 'Contrat à Durée Déterminée')], default='CDI', max_length=50),
        ),
        migrations.AlterField(
            model_name='departement',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='departement',
            name='nom',
            field=models.CharField(default='Non spécifié', max_length=255),
        ),
        migrations.AlterField(
            model_name='employe',
            name='contrat',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.contrat'),
        ),
        migrations.AlterField(
            model_name='employe',
            name='date_embauche',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='employe',
            name='departement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.departement'),
        ),
        migrations.AlterField(
            model_name='employe',
            name='email',
            field=models.EmailField(db_index=True, default='inconnu@example.com', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='employe',
            name='nom',
            field=models.CharField(default='Inconnu', max_length=255),
        ),
        migrations.AlterField(
            model_name='employe',
            name='prenom',
            field=models.CharField(default='Inconnu', max_length=255),
        ),
        migrations.AlterField(
            model_name='employe',
            name='salaire_actuel',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='employe',
            name='telephone',
            field=models.CharField(default='0000000000', max_length=20),
        ),
        migrations.AlterField(
            model_name='employeconge',
            name='conge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.conge'),
        ),
        migrations.AlterField(
            model_name='employeconge',
            name='employe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.employe'),
        ),
        migrations.AlterField(
            model_name='offreemploi',
            name='date_expiration',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='offreemploi',
            name='date_publication',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='offreemploi',
            name='departement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.departement'),
        ),
        migrations.AlterField(
            model_name='offreemploi',
            name='description',
            field=models.TextField(default='Aucune description'),
        ),
        migrations.AlterField(
            model_name='offreemploi',
            name='titre',
            field=models.CharField(default='Offre sans titre', max_length=255),
        ),
        migrations.AlterField(
            model_name='performance',
            name='commentaire',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='performance',
            name='employe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.employe'),
        ),
        migrations.AlterField(
            model_name='performance',
            name='objectif',
            field=models.CharField(default='Non spécifié', max_length=255),
        ),
        migrations.AlterField(
            model_name='performance',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='role',
            name='nom_role',
            field=models.CharField(default='Employé', max_length=255),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='role',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pages.role'),
        ),
    ]
