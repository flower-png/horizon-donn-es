import pandas as pd

# ── 1. Chargement du fichier CSV d'Airbnb ────────────────────────────────────
fichier_airbnb = "listings.csv"
print("Chargement des données Airbnb...")
df_airbnb = pd.read_csv(fichier_airbnb)
print(f"Taille avant nettoyage : {len(df_airbnb)} annonces brutes trouvées.")

# ── 2. Sélection des colonnes utiles ─────────────────────────────────────────
# On ajoute 'price' et 'minimum_nights' par rapport à l'original
colonnes_utiles = [
    'latitude',
    'longitude',
    'neighbourhood_cleansed',
    'room_type',
    'price',
    'minimum_nights',       # utile pour identifier les locations long-terme déguisées
]
df_reduit = df_airbnb[colonnes_utiles]

# ── 3. Filtrage : logements entiers seulement ─────────────────────────────────
# Louer une chambre simple ne retire pas un logement du marché locatif
df_clean = df_reduit[df_reduit['room_type'] == 'Entire home/apt'].copy()
print(f"\nLogements entiers (Entire home/apt) : {len(df_clean)} annonces.")

# ── 4. Nettoyage du prix ──────────────────────────────────────────────────────
# Le prix dans Inside Airbnb est formaté comme "$150.00" → on enlève $ et virgules
df_clean['price'] = (
    df_clean['price']
    .str.replace(r'[$,]', '', regex=True)
    .astype(float)
)

# Enlever les prix aberrants (gratuit ou > 2000$/nuit)
nb_avant = len(df_clean)
df_clean = df_clean[
    (df_clean['price'] > 0) &
    (df_clean['price'] <= 2000)
]
print(f"Après filtre prix (0$ < prix <= 2000$) : {len(df_clean)} annonces.")
print(f"  ({nb_avant - len(df_clean)} annonces retirées pour prix aberrant)")

# ── 5. Renommer les colonnes ──────────────────────────────────────────────────
df_clean.columns = [
    'Latitude',
    'Longitude',
    'Quartier',
    'Type_Logement',
    'Prix_Nuit',
    'Nuits_Minimum',
]

# ── 6. Statistiques par quartier ─────────────────────────────────────────────
print("\n=== Statistiques par quartier ===")
stats_quartier = df_clean.groupby('Quartier').agg(
    Airbnb_Count  = ('Prix_Nuit', 'count'),
    Prix_Median   = ('Prix_Nuit', 'median'),
    Prix_Moyen    = ('Prix_Nuit', 'mean'),
    Prix_Min      = ('Prix_Nuit', 'min'),
    Prix_Max      = ('Prix_Nuit', 'max'),
).reset_index()

stats_quartier['Prix_Moyen'] = stats_quartier['Prix_Moyen'].round(2)
print(stats_quartier.sort_values('Airbnb_Count', ascending=False).to_string(index=False))

# ── 7. Affichage du résultat global ──────────────────────────────────────────
print(f"\n=== Résumé global ===")
print(f"Total annonces retenues    : {len(df_clean)}")
print(f"Prix médian par nuit       : {df_clean['Prix_Nuit'].median():.0f} $")
print(f"Prix moyen par nuit        : {df_clean['Prix_Nuit'].mean():.0f} $")
print(f"Nombre de quartiers        : {df_clean['Quartier'].nunique()}")

# ── 8. Sauvegarde des fichiers ────────────────────────────────────────────────

# Fichier principal avec tous les listings (pour spatial join dans agg_quartiers.ipynb)
nom_fichier_propre = "airbnb_montreal_PROPRE.csv"
df_clean.to_csv(nom_fichier_propre, index=False, encoding='utf-8-sig')
print(f"\n✅ Fichier listings sauvegardé       : {nom_fichier_propre}")

# Fichier agrégé par quartier (pour jointure directe si besoin)
nom_fichier_stats = "airbnb_montreal_stats_quartier.csv"
stats_quartier.to_csv(nom_fichier_stats, index=False, encoding='utf-8-sig')
print(f"✅ Fichier stats quartier sauvegardé : {nom_fichier_stats}")