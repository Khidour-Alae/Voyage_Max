# Utilise une image officielle Python 3.10 comme parent
FROM python:3.10-slim

# Définis le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier des dépendances et installe-les
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copie le reste de votre code d'application dans le conteneur
COPY . .

# Expose le port sur lequel l'application s'exécute
EXPOSE 8050

# Commande pour exécuter l'application
CMD ["python", "./train_app/app.py"]
