from flask import Flask, render_template, request
import pandas as pd
import requests
import folium
import os
import json


#############################################
############### PARTIE TRAINS ###############
#############################################

RESULTATS_GLOBAUX = None
app = Flask(__name__)

def rechercher_tgvmax(ville_depart, date1, date2 = None):
    if date2 == None:
        date2 = date1

    api_url = f"""https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/tgvmax/records?
                  select=date%2Corigine%2Cdestination%2Cheure_depart%2Cheure_arrivee&
                  where=date%20%3E%3D%20%22{date1}%22%20and%20date%20%3C%3D%20%22{date2}%22%20and%20
                  search(origine%2C%20%22{ville_depart}%22)&
                  order_by=date%2Cheure_depart&refine=od_happy_card%3A%22NON%22"""


    all_records = []
    offset = 0
    limit = 100

    while True:
        params = {
            "limit": limit,
            "offset": offset
        }
        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            data = response.json()
            records = data.get('results', [])
            all_records.extend(records)

            # Vérifier s'il y a plus de pages à récupérer
            if len(records) < limit:
                break

            offset += limit
        else:
            print(f"Erreur {response.status_code} : {response.text}")
            break
    df_trains = pd.DataFrame(all_records)
    return df_trains

def filtrer_aller_retour_possible(row):
    date_aller = pd.to_datetime(row['Date Aller'] + ' ' + row['Heure Arrivée Aller'])
    date_retour = pd.to_datetime(row['Date Retour'] + ' ' + row['Heure Départ Retour'])

    return date_aller <= date_retour

def rechercher_tgvmax_aller_retour(ville_depart, date_depart1, date_retour1, date_depart2 = None, date_retour2 = None):

    df_allers = rechercher_tgvmax(ville_depart, date_depart1, date_depart2)
    col = df_allers.columns
    df_allers.rename(columns=lambda x: f"{x}_aller", inplace = True)

    liste_des_villes_possibles = df_allers["destination_aller"].unique()

    df_retours = pd.DataFrame(columns = col )
    df_retours.rename(columns=lambda x: f"{x}_retour", inplace = True)

    for destination in liste_des_villes_possibles:
      df_retour = rechercher_tgvmax(destination, date_retour1, date_retour2)
      if not df_retour.empty:
        df_retour.rename(columns=lambda x: f"{x}_retour", inplace = True)
        df_retour = df_retour[df_retour["destination_retour"].str.contains(ville_depart, case=False, na=False)]
        df_retours = pd.concat([df_retours, df_retour], axis = 0)

    df_final = pd.merge(df_allers, df_retours, left_on='destination_aller', right_on='origine_retour')

    df_final.drop(["origine_retour", "destination_retour"], axis = 1, inplace = True)
    df_final.rename(columns={"date_aller": "Date Aller",
                             "date_retour": "Date Retour",
                             "origine_aller" : "Ville de Départ",
                             "destination_aller" : "Destination",
                             "heure_depart_aller" : "Heure Départ Aller",
                             "heure_depart_retour" : "Heure Départ Retour",
                             "heure_arrivee_aller" : "Heure Arrivée Aller",
                             "heure_arrivee_retour" : "Heure Arrivée Retour"
                             }, inplace = True)

    df_final = df_final[df_final.apply(filtrer_aller_retour_possible, axis=1)]

    return df_final.drop_duplicates()

def liste_villes(df):
    return sorted(df["Destination"].unique())

def filtrer_ville(df,ville):
    return df[df["Destination"] == ville]

##############################################
################ PARTIE CARTE ################
##############################################

def extraire_nom_ville(nom_complet):
    # Diviser le nom complet en fonction du premier caractère spécial trouvé
    if '(' in nom_complet:
        mots = nom_complet.split('(', 1)
    elif ' -' in nom_complet:
        mots = nom_complet.split(' -', 1)
    elif '-' in nom_complet:
        mots = nom_complet.split('-', 1)
    else:
        mots = [nom_complet]

    # Retourner le premier mot (après avoir supprimé les espaces inutiles)
    return mots[0].strip()



def carte(df, fichier_json='liste_gares.json'):
    # Construire le chemin absolu vers le fichier JSON
    chemin_dossier = os.path.dirname(__file__)  # Obtient le chemin du dossier contenant app.py
    chemin_complet = os.path.join(chemin_dossier, 'data', fichier_json)  # Construit le chemin vers le fichier JSON

    # Charger le fichier JSON contenant les coordonnées des gares
    coordonnees_gares = {}
    if os.path.exists(chemin_complet):
        with open(chemin_complet, 'r', encoding='utf-8') as f:
            coordonnees_gares = json.load(f)

    # Créer une carte centrée sur la France
    map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Vérifier si le DataFrame n'est pas vide avant d'ajouter des marqueurs
    if not df.empty:
        gares = df["Destination"].unique()
        gares_df = pd.DataFrame(columns=['Gare', 'Latitude', 'Longitude'])

        # Obtenir les coordonnées de chaque gare directement à partir du JSON
        for gare in gares:
            if gare in coordonnees_gares:
                coordonnees = coordonnees_gares[gare]
                gares_df = pd.concat([gares_df, pd.DataFrame([{'Gare': gare,
                                                                'Latitude': coordonnees['latitude'],
                                                                'Longitude': coordonnees['longitude']}])], ignore_index=True)

        # Ajouter des marqueurs pour chaque gare
        for index, row in gares_df.iterrows():
            folium.Marker([row['Latitude'], row['Longitude']], popup=row['Gare']).add_to(map)

        # Ajouter un marqueur pour la ville de départ si elle est présente dans les coordonnées des gares
        if "Ville de Départ" in df.columns and df["Ville de Départ"].unique().size > 0:
            ville_depart = df["Ville de Départ"].unique()[0]
            if ville_depart in coordonnees_gares:
                location_depart = coordonnees_gares[ville_depart]
                folium.Marker([location_depart['latitude'], location_depart['longitude']], 
                              popup=ville_depart, 
                              icon=folium.Icon(color='red')).add_to(map)

    return map



##############################################
################ PARTIE FLASK ################
##############################################

@app.route('/')
def index():
    return render_template('index.html')  # À créer plus tard
@app.route('/recherche', methods=['POST'])

@app.route('/recherche', methods=['POST'])
def recherche():
    global RESULTATS_GLOBAUX
    
    ville_depart = request.form['ville_depart']

    date_aller1 = request.form['date_aller1']
    date_aller2 = request.form.get('date_aller2') or date_aller1  # Utilise date_aller1 si date_aller2 n'est pas renseigné

    date_retour1 = request.form['date_retour1']
    date_retour2 = request.form.get('date_retour2') or date_retour1  # Utilise date_retour1 si date_retour2 n'est pas renseigné

    RESULTATS_GLOBAUX = rechercher_tgvmax_aller_retour(extraire_nom_ville(ville_depart), date_aller1, date_retour1, date_aller2, date_retour2)
    if not RESULTATS_GLOBAUX.empty:
        villes_accessibles = liste_villes(RESULTATS_GLOBAUX)
        carte_html = carte(RESULTATS_GLOBAUX)._repr_html_()
    else:
        villes_accessibles = []
        carte_html = folium.Map(location=[46.603354, 1.888334], zoom_start=6)._repr_html_()  # Carte vide

    return render_template('resultats.html', villes=villes_accessibles, carte=carte_html)


@app.route('/resultat-<ville>')
def resultat_ville(ville):
    resultats_filtrés = filtrer_ville(RESULTATS_GLOBAUX, ville)  # Assurez-vous d'avoir accès à `resultats_globaux` ici
    return render_template('resultat_ville.html', resultats=resultats_filtrés.to_dict('records'), ville=ville)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
