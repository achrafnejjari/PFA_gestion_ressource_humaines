from django.db import models

# 1. Utilisateur et Role (Relation 1:1)
class Role(models.Model):
    nom_role = models.CharField(max_length=255)

    def __str__(self):
        return self.nom_role


class Utilisateur(models.Model):
    nom_utilisateur = models.CharField(max_length=255)
    mot_de_passe = models.CharField(max_length=255)
    role = models.OneToOneField(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom_utilisateur


# 2. Employé (Relation avec Contrat, Département, Performance)
class Departement(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.nom


class Contrat(models.Model):
    type = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    salaire_initial = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.type} - {self.date_debut}"


class Employe(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    salaire_actuel = models.DecimalField(max_digits=10, decimal_places=2)
    date_embauche = models.DateField()
    contrat = models.OneToOneField(Contrat, on_delete=models.CASCADE)
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# 3. Performance (Relation N:1 avec Employé)
class Performance(models.Model):
    objectif = models.CharField(max_length=255)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    commentaire = models.TextField()
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)

    #debut_objectif = models.DateField()  # Nouveau champ
    #fin_objectif = models.DateField()    # Nouveau champ
    
    #cette fonction peux aide au colum de period objectif quand tu veux le afiche dans la page html 
    # def periode_objectif(self):
    #     # Calcule la période en mois (approximative)
    #     delta = (self.fin_objectif - self.debut_objectif).days
    #     mois = delta // 30  # Approximation (30 jours par mois)
    #     return f"{mois} mois"

    def __str__(self):
        return f"Performance de {self.employe.nom} - Score: {self.score}"




# 4. Congé (Relation N:M avec Employé)
class Conge(models.Model):
    type = models.CharField(max_length=50)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.type} - {self.statut}"


class EmployeConge(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    conge = models.ForeignKey(Conge, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('employe', 'conge')  # chaque emplyee a son conge unique

    def __str__(self):
        return f"{self.employe.nom} - {self.conge.type}"


# 5. Offre d'Emploi (Relation N:1 avec Département)
class OffreEmploi(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    date_publication = models.DateField()
    date_expiration = models.DateField()
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titre} - {self.departement.nom}"


# 6. Candidat et Candidature (Relation N:M entre Candidat et Offre d'Emploi)
class Candidat(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20)
    cv = models.FileField(upload_to='cv/')

    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Candidature(models.Model):
    date_submission = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50) #"En attente", "Acceptée", "Rejetée"
    candidat = models.ForeignKey(Candidat, on_delete=models.CASCADE)
    offre_emploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('candidat', 'offre_emploi')

    def __str__(self):
        return f"Candidature de {self.candidat.nom} pour {self.offre_emploi.titre}"