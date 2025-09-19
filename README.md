# 📌 TeamCore – Gestion des Ressources Humaines avec Chatbot IA
## 📖 Description

TeamCore est une application web développée dans le cadre d’un Projet de Fin d’Année (PFA) à SUPMTI Oujda.
Elle a pour objectif de fournir une solution digitale moderne et complète pour la gestion des ressources humaines d’une entreprise fictive.

L’application intègre :

Un système de gestion interne (employés, départements, contrats, congés, performances).

Une gestion des offres d’emploi et des candidatures.

Une interface publique pour les visiteurs.

Un Chatbot IA permettant de répondre automatiquement aux questions des visiteurs.

# 🚀 Fonctionnalités principales

## Administrateurs / RH :

Gestion des employés, contrats, congés, départements.

Suivi des performances et activités annuelles.

Publication et suivi des offres d’emploi et candidatures.

Génération de rapports PDF.

## Employés :

Accès à un espace personnel sécurisé.

Consultation de leurs tâches et mise à jour de leurs actions.

Demande de congé et attente d’acceptation.

Accès à des certifications à étudier, fournies par l’entreprise, si le service RH publie certaines certifications sur le site.

## Visiteurs :

Consultation des offres d’emploi.

Interaction avec un Chatbot IA pour obtenir des réponses rapides.

Possibilité de postuler en ligne.

# 🛠️ Technologies utilisées

Backend : Django (Python)

Frontend : HTML, CSS, Bootstrap, JavaScript

Base de données : MySQL

IA : Intégration d’un Chatbot basé sur l’IA

Outils : Docker, Git, Jira, VS Code

Conception : Figma (UI/UX), Draw.io (UML)

# 📂 Organisation du projet

my_project/ → Code source de l’application Django.

templates/ → Interfaces utilisateur.

static/ → Ressources (CSS, JS, images).

chatbot/ → Module IA intégré.

migrations/ → Gestion des modèles et base de données.

# ⚙️ Installation et exécution

### Cloner le dépôt

git clone https://github.com/achrafnejjari/PFA_gestion_ressource_humaines.git
cd PFA_gestion_ressource_humaines



### Installer les dépendances

pip install -r requirements.txt

### Construire les images Docker
docker-compose build

### Lancer les conteneurs
docker-compose up -d

### Lancer le serveur

docker-compose exec web python manage.py runserver




# ✨ Auteurs

👨‍💻 Réalisé par Achraf Nejjari et Tarek Bekkaoui –PFA en 2025 .
