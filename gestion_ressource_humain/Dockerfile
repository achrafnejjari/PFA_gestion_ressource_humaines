# Utilisation d'une image légère de Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour MySQL et pkg-config
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet Django dans le conteneur
COPY . /app/

# Exposer le port sur lequel Django va tourner
EXPOSE 8081

# Commande pour démarrer Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8081"]
