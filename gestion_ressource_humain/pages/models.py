from django.db import models
from django.contrib.auth.models import User
from datetime import date

# 1. Utilisateur et Role
class Role(models.Model):
    nom_role = models.CharField(max_length=255, default="Employé")

    def __str__(self):
        return self.nom_role

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

class Utilisateur(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    url_photo = models.URLField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        null=True,  # Nullable temporairement pour migration
        blank=True
    )

    def __str__(self):
        return self.user.username if self.user else "Utilisateur sans user"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

# 2. Employé, Département, Contrat
class Departement(models.Model):
    nom = models.CharField(max_length=255, default="Non spécifié")  # Valeur par défaut
    description = models.TextField(blank=True)  # Facultatif

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"   


class Contrat(models.Model):
    TYPE_CHOICES = [
        ('CDI', 'Contrat à Durée Indéterminée'),
        ('CDD', 'Contrat à Durée Déterminée'),
        ('Stage', 'Stage'),
        ('Freelance', 'Freelance'),
    ]
    leave_entitlement = models.IntegerField(default=25, verbose_name="Jours de congé annuels")
    contract_id = models.CharField(max_length=10, unique=True, blank=True, verbose_name="Identifiant du contrat")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='CDI', verbose_name="Type de contrat")

    def save(self, *args, **kwargs):
        if not self.contract_id:
            last_contrat = Contrat.objects.order_by('-id').first()
            next_id = (last_contrat.id + 1) if last_contrat else 1
            self.contract_id = f"C{next_id:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        employe = Employe.objects.filter(contrat=self).first()
        return f"{self.contract_id} - {employe.nom if employe else 'Sans employé'}"

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"

class Employe(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        null=True,  # Nullable temporairement pour la migration
        blank=True
    )
    nom = models.CharField(max_length=255, default="Inconnu")  # Valeur par défaut
    prenom = models.CharField(max_length=255, default="Inconnu")  # Valeur par défaut
    date_de_naissance = models.DateField(default=date(2000, 1, 1))  # Valeur par défaut
    email = models.EmailField(unique=True, db_index=True, default="inconnu@example.com")  # Valeur par défaut
    telephone = models.CharField(max_length=20, default="0000000000")  # Valeur par défaut
    salaire_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Valeur par défaut
    date_embauche = models.DateField(default=date.today)  # Valeur par défaut
    date_fin = models.DateField(blank=True, null=True)  # Facultatif
    contrat = models.OneToOneField(Contrat, on_delete=models.CASCADE, null=True)  # Nullable temporairement
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE, null=True)  # Nullable temporairement

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['nom', 'prenom']

# 3. Performance
class Performance(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, null=True)  # Nullable temporairement
    objectif = models.CharField(max_length=255, default="Non spécifié")  # Valeur par défaut
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Valeur par défaut
    commentaire = models.TextField(blank=True)  # Facultatif
    debut_objectif = models.DateField(default=date.today)  # Valeur par défaut
    fin_objectif = models.DateField(default=date.today)  # Valeur par défaut
    date_evaluation = models.DateField(blank=True, null=True)  # Facultatif

    def periode_objectif(self):
        if self.fin_objectif and self.debut_objectif:
            delta = (self.fin_objectif - self.debut_objectif).days
            if delta < 0:
                return "Non défini"  # Si la date de fin est avant la date de début
            elif delta < 30:
                return f"{delta} jours"  # Moins d'un mois, afficher seulement les jours
            else:
                mois = delta // 30
                jours = delta % 30
                if jours == 0:
                    return f"{mois} mois"  # Exactement un nombre de mois
                return f"{mois} mois et {jours} jours"  # Mois et jours restants
        return "Non défini"

    def __str__(self):
        return f"Performance de {self.employe.nom if self.employe else 'Inconnu'} - Score: {self.score}"

    class Meta:
        verbose_name = "Performance"
        verbose_name_plural = "Performances"

# 4. Congé (Relation N:M avec Employé)
class Conge(models.Model):
    type = models.CharField(max_length=50, default="Congé annuel") 
    date_debut = models.DateField(default=date.today)
    date_fin = models.DateField(default=date.today)
    statut = models.CharField(
        max_length=50,
        choices=[('EN_ATTENTE', 'En attente'), ('APPROUVE', 'Approuvé'), ('REFUSE', 'Refusé')],
        default='EN_ATTENTE'
    )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.statut}"

    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"

class EmployeConge(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, null=True)  # Nullable temporairement
    conge = models.ForeignKey(Conge, on_delete=models.CASCADE, null=True)  # Nullable temporairement

    class Meta:
        unique_together = ('employe', 'conge')
        verbose_name = "Employé-Congé"
        verbose_name_plural = "Employés-Congés"

    def __str__(self):
        return f"{self.employe.nom if self.employe else 'Inconnu'} - {self.conge.type if self.conge else 'Inconnu'}"

# 5. Offre d'Emploi
class OffreEmploi(models.Model):
    STATUT_CHOICES = [
        ('OUVERTE', 'Ouverte'),
        ('FERMEE', 'Fermée'),
    ]

    titre = models.CharField(max_length=100)
    description = models.TextField()
    date_publication = models.DateField()
    date_expiration = models.DateField()
    competences_requises = models.TextField(blank=True, null=True, help_text="Compétences requises pour le poste.")
    salaire = models.CharField(max_length=50, blank=True, null=True, help_text="Salaire proposé (ex. 30k-40k EUR/an).")
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='OUVERTE')

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = "Offre d'emploi"
        verbose_name_plural = "Offres d'emploi"

# 6. Candidat et Candidature
class Candidat(models.Model):
    nom = models.CharField(max_length=255, default="Inconnu")  # Valeur par défaut
    prenom = models.CharField(max_length=255, default="Inconnu")  # Valeur par défaut
    email = models.EmailField(unique=True, db_index=True, default="candidat@example.com")  # Valeur par défaut
    telephone = models.CharField(max_length=20, default="0000000000")  # Valeur par défaut
    cv = models.FileField(upload_to='cv/', null=True, blank=True)  # Nullable temporairement

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"

class Candidature(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('ACCEPTEE', 'Acceptée'),
        ('REJETEE', 'Rejetée'),
    ]
    date_submission = models.DateField(auto_now_add=True)
    statut = models.CharField(
        max_length=50,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'  # Valeur par défaut
    )
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE, null=True)  # Nullable temporairement
    offre_emploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, null=True)  # Nullable temporairement

    class Meta:
        unique_together = ('candidat', 'offre_emploi')
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"

    def __str__(self):
        return f"Candidature de {self.candidat.nom if self.candidat else 'Inconnu'} pour {self.offre_emploi.titre if self.offre_emploi else 'Inconnu'}"
    


class Training(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class TrainingRegistration(models.Model):
    employee = models.ForeignKey('Employe', on_delete=models.CASCADE)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    registered_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.nom} - {self.training.title}"
    

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']