# Voyage Max

Voyage Max est une application web développée avec Python et Flask, conçue pour les utilisateurs de l'abonnement TGV Max de la SNCF. 
Elle permet de trouver, à partir d'une ville de départ et de dates de voyage données, l'ensemble des destinations accessibles gratuitement grâce à l'abonnement TGV Max. 
Les utilisateurs peuvent visualiser ces villes sur une carte, cliquer sur une ville pour explorer les trajets aller-retour disponibles, et spécifier des intervalles de dates pour l'aller et/ou le retour afin de trouver les trains correspondant à leurs plans de voyage.

## Fonctionnalités

- Recherche de destinations TGV Max à partir d'une ville de départ et de dates de voyage.
- Affichage des villes accessibles sur une carte interactive.
- Exploration détaillée des trajets aller-retour possibles pour chaque destination.
- Support de la recherche flexible avec des intervalles de dates pour l'aller et/ou le retour.

## Remarques:

Le temps d'exécution est proportionnelle aux nombres de villes explorables à partir de la ville de départ et la période choisie, grand intervalle de dates = grand nombre de trajet --> temps d'exéctution plus grand. Donc ça peut aller de quelques secondes à quelques minutes pour les grandes villes comme Paris, Lyon ... ou quand la plage de dates est grande aussi. 

## Technologies Utilisées

- Python
- Flask
- Pandas pour le traitement des données
- Folium pour la génération de cartes interactives
- Requêtes API à la SNCF pour récupérer les informations de voyage
- Docker pour le déploiement sur une VM

## Installation et Déploiement avec Docker

Pour construire et exécuter Voyage Max dans un conteneur Docker, suivez ces étapes :

1. Lancer install.sh puis launch.sh

2. Si ça ne marche pas **Construire l'image Docker**

   À partir du répertoire contenant le Dockerfile, exécutez la commande suivante pour construire votre image Docker :

   ```bash
   docker build -t tgvmax_app .

   docker run -p 8050:8050 tgvmax_app



