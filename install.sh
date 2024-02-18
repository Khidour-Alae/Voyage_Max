#!/bin/bash

# Construire l'image Docker à partir du Dockerfile présent dans le dossier courant
# Le nom de l'image sera tgvmax_app
docker build -t tgvmax_app .

# Afficher les images Docker pour confirmer la création
docker images
