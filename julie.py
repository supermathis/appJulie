import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium

# Charger les données des missions depuis un fichier CSV
def load_data():
    try:
        return pd.read_csv('missions.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Titre', 'Description', 'Date', 'Heure', 'Emplacement', 'Latitude', 'Longitude', 'Durée'])

# Enregistrer les données des missions dans un fichier CSV
def save_data(df):
    df.to_csv('missions.csv', index=False)

# Ajouter une nouvelle mission
def add_mission(titre, description, date, heure, emplacement, duree, latitude=None, longitude=None):
    df = load_data()
    new_mission = pd.DataFrame([[titre, description, date, heure, emplacement, latitude, longitude, duree]],
                               columns=['Titre', 'Description', 'Date', 'Heure', 'Emplacement', 'Latitude', 'Longitude', 'Durée'])
    df = pd.concat([df, new_mission], ignore_index=True)
    save_data(df)
    return df

# Définir les lieux prédéfinis avec des coordonnées approximatives
coordinates = {
    "AFFUT 57": (),
    "Aire TransBordement" : (),
    "Brin 05 Nord": (43.097279, 6.144623),
    "Brin 05 Sud": (43.096369, 6.145568),
    "Brin 23 Nord": (43.105131, 6.158031),
    "Brin 23 Sud": (43.104272, 6.159033),    
    "Décanteur seuil 05" : (),
    "Décanteur seuil 23" : (),
    "Décanteur seuil 31" : (),
    "Décanteur seuil 13" : (),
    "DF301 Météo" : (),
    "Douane" : (43.088860, 6.151467),
    "Gendarmerie" : (43.089045, 6.150516),
    "Glide ILS": (43.096172, 6.146409), 
    "Gonio" : (43.100976, 6.142605),
    "LOC ILS" : (43.106242,6.162347),
    "Mat Météo seuil 31" : (43.091080, 6.153183),
    "Mat Météo seuil 05" : (43.095758, 6.144676),
    "Mat Météo seuil 23" : (43.106222, 6.162340),
    "PAR" : (43.097970, 6.148583),
    "Park Instrument Météo" : (),
    "Poste P9" : (),
    "Station émission radio" : (43.088519, 6.153178),
    "TACAN" : (43.100309, 6.147642),
    "Télémètre à l'image" : ()
}


# Interface utilisateur avec Streamlit
st.title("Gestion des Missions de la BAN de Hyères")

# Formulaire pour ajouter une nouvelle mission
with st.form("add_mission_form"):
    st.header("Ajouter une nouvelle mission")
    titre = st.text_input("Titre")
    description = st.text_area("Description")
    date = st.date_input("Date")
    heure = st.time_input("Heure")
    emplacement = st.selectbox("Emplacement", options=list(coordinates.keys()))
    duree = st.number_input("Durée (en heures)", format="%f")
    submitted = st.form_submit_button("Ajouter Mission")
    if submitted:
        # Convertir la date en string format 'YYYY-MM-DD'
        date_str = date.strftime('%Y-%m-%d')
        # Convertir l'heure en string format 'HH:MM:SS'
        heure_str = heure.strftime('%H:%M:%S')
        # Récupérer les coordonnées correspondant à l'emplacement sélectionné
        latitude, longitude = coordinates.get(emplacement, (None, None))
        df = add_mission(titre, description, date_str, heure_str, emplacement,duree, latitude, longitude)
        st.success("Mission ajoutée avec succès!")
    else:
        df = load_data()

# Générer les 6 prochains jours
today = datetime.today().date()
next_6_days = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6)]

# Menu déroulant pour sélectionner la date
selected_date_str = st.sidebar.selectbox("Sélectionner la date", next_6_days)
selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d')

# Filtrer les missions pour la date sélectionnée
df_filtered = df[df['Date'] == selected_date_str].sort_values(by='Heure')
st.header(f"Missions of {selected_date.strftime('%A %d %B %Y')}")

# Afficher la liste des missions pour la date sélectionnée
if not df_filtered.empty:
    for _, row in df_filtered.iterrows():
        with st.container():
            st.markdown(f"""
        <div style="border: 2px solid #1E90FF; border-radius: 5px; padding: 5px; margin-bottom: 5px; background-color: #f9f9f9;">
            <h3 style="color: #1E90FF; font-size: 16px; margin-bottom: 5px;">{row['Titre']}</h3>
            <p style="color: #1E90FF;font-size: 14px; margin-bottom: 5px;"><strong>Description:</strong> {row['Description']}</p>
            <p style="color: #1E90FF;font-size: 14px; margin-bottom: 5px;"><strong>Heure:</strong> {row['Heure']}</p>
            <p style="color: #1E90FF;font-size: 14px; margin-bottom: 5px;"><strong>Emplacement:</strong> {row['Emplacement']}</p>
            <p style="color: #1E90FF;font-size: 14px; margin-bottom: 5px;"><strong>Durée:</strong> {row['Durée']} heures</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.write("Aucune mission prévue pour ce jour.")

# Créer une carte avec Folium pour les missions du jour
map_center = [43.098, 6.146]  # Coordonnées approximatives de l'aéroport de Hyères
m = folium.Map(location=map_center, zoom_start=14)

# Ajouter les missions à la carte
for _, row in df_filtered.iterrows():
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        bounds = [
            [row['Latitude'] - 0.001, row['Longitude'] - 0.001],
            [row['Latitude'] + 0.001, row['Longitude'] + 0.001]
        ]
        popup_content = f"""
        <strong>{row['Titre']}</strong><br>
        Description: {row['Description']}<br>
        Date: {row['Date']}<br>
        Heure: {row['Heure']}<br>
        Emplacement: {row['Emplacement']}<br>
        Durée: {row['Durée']} heures
        """
        folium.Rectangle(
            bounds,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.1,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(m)
    else:
        # Gérer l'affichage pour les lieux sans coordonnées GPS
        # Ici, nous utilisons les coordonnées approximatives définies dans 'coordinates'
        if row['Emplacement'] in coordinates:
            coord = coordinates[row['Emplacement']]
            folium.Marker(
                location=coord,
                popup=row['Emplacement'],
                icon=folium.Icon(color='blue')
            ).add_to(m)

st_folium(m, width=900, height=700)









