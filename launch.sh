#!/bin/bash

# Supprimer le conteneur précédent s'il existe
docker rm -f mon_conteneur_tgvmax_app

# Lancer un nouveau conteneur à partir de l'image tgvmax_app
docker run -d -p 8050:8050 --name mon_conteneur_tgvmax_app tgvmax_app:latest

# Vérifier si le conteneur démarre correctement
docker ps -a

# Afficher les logs du conteneur pour s'assurer qu'il n'y a pas d'erreurs au démarrage
docker logs mon_conteneur_tgvmax_app
