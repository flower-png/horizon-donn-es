import pandas as pd
import geopandas as gpd

# =========================================================
# 0. CHARGEMENT
# =========================================================

airbnb      = pd.read_csv("airbnb_montreal_PROPRE.csv")
permis      = pd.read_csv("permis_aggregation_arrondissement.csv")
ct          = pd.read_csv("ct_arrondissement_features.csv")
evic_media  = pd.read_csv("evictions_media_arr_mtl.csv")
evic_rclalq = pd.read_csv("evictions_montreal_rclalq.csv", sep=";")
arr_gdf     = gpd.read_file("arrondissements_mtl.geojson")

# =========================================================
# 1. ÉVICTIONS
# =========================================================

evic_media = evic_media[["Arrondissement", "Nombre_Articles"]].copy()
evic_media.columns = ["NOM", "Evictions_Media_Count"]
evic_media["NOM"] = evic_media["NOM"].str.strip()

evic_rclalq = evic_rclalq[["Arrondissement", "Evictions_Proxy_2023"]].copy()
evic_rclalq.columns = ["NOM", "Evictions_RCLALQ_2023"]
evic_rclalq["NOM"] = evic_rclalq["NOM"].str.strip()

evictions = evic_media.merge(evic_rclalq, on="NOM", how="outer")
print("=== ÉVICTIONS ===")
print(evictions)

# =========================================================
# 2. AIRBNB → ARRONDISSEMENT
# =========================================================

arr_proj = arr_gdf[["NOM", "geometry"]].to_crs("EPSG:3347")

airbnb_gdf = gpd.GeoDataFrame(
    airbnb,
    geometry=gpd.points_from_xy(airbnb.Longitude, airbnb.Latitude),
    crs="EPSG:4326"
).to_crs("EPSG:3347")

airbnb_arr = gpd.sjoin(airbnb_gdf, arr_proj, how="left", predicate="within")

airbnb_agg = airbnb_arr.groupby("NOM").agg(
    Airbnb_Count=("NOM", "count")
).reset_index()

if "Prix_Nuit" in airbnb.columns:
    prix_agg = airbnb_arr.groupby("NOM").agg(
        Airbnb_Median_Price=("Prix_Nuit", "median")
    ).reset_index()
    airbnb_agg = airbnb_agg.merge(prix_agg, on="NOM", how="left")

print(f"\n=== AIRBNB ===")
print(airbnb_agg.head())

# =========================================================
# 3. PERMIS (RENOVICTIONS)
# =========================================================

permis_16_21 = permis[
    (permis["annee"] >= 2016) & (permis["annee"] <= 2021)
].groupby("arrondissement").agg(
    Permis_Renovation=("nb_permis", "sum")
).reset_index().rename(columns={"arrondissement": "NOM"})

# =========================================================
# 4. SOCIO-ÉCO
# =========================================================

ct_features = ct.rename(columns={"arrondissement": "NOM"})

# =========================================================
# 5. MERGE FINAL
# =========================================================

df_final = arr_gdf[["NOM"]].copy()
df_final = df_final \
    .merge(evictions,    on="NOM", how="left") \
    .merge(airbnb_agg,   on="NOM", how="left") \
    .merge(permis_16_21, on="NOM", how="left") \
    .merge(ct_features,  on="NOM", how="left")

# Arrondissement officiels MTL
arrondissements_officiels = [
    "Ahuntsic-Cartierville",
    "Anjou",
    "Côte-des-Neiges-Notre-Dame-de-Grâce",
    "Lachine",
    "LaSalle",
    "Le Plateau-Mont-Royal",
    "Le Sud-Ouest",
    "Mercier-Hochelaga-Maisonneuve",
    "Montréal-Nord",
    "Outremont",
    "Pierrefonds-Roxboro",
    "Rivière-des-Prairies-Pointe-aux-Trembles",
    "Rosemont-La Petite-Patrie",
    "Saint-Laurent",
    "Saint-Léonard",
    "Verdun",
    "Ville-Marie",
    "Villeray-Saint-Michel-Parc-Extension"
]

df_final = df_final[
    df_final["NOM"].isin(arrondissements_officiels)
]

print(f"\n=== MERGE FINAL : {len(df_final)} arrondissements ===")

# =========================================================
# 6. VARIABLES FINALES
# =========================================================

colonnes_voulues = [
    "NOM",
    # Variable dépendante
    "Evictions_RCLALQ_2023",
    "Evictions_Media_Count",
    # Pression du marché
    "Airbnb_Count",
    "Airbnb_Median_Price",
    "Augmentation_Loyer_16_21",
    "Augmentation_Valeur_16_21",
    # Vulnérabilité
    "Delta_Ratio_Loyer_Revenu",
    "Ratio_Loyer_Revenu_2021",
    "pct_locataires_2021",
    "pct_loc_30plus_2021",
    "revenu_median_2021",
    "faible_revenu_pct_2021",
    # Mécanismes
    "Permis_Renovation",
    # Structure sociale
    "pct_immigrants_rec_2021",
    "densite_2021",
    "croissance_pop_16_21",
    "age_moyen_2021",
    # Supplémentaires
    "loyer_median_2021",
    "loyer_median_2016",
    "valeur_logement_2021",
    "valeur_logement_2016",
    "Augmentation_Revenu_16_21",
    "Delta_Pct_Locataires",
    "Delta_Faible_Revenu",
]

colonnes_dispo    = [c for c in colonnes_voulues if c in df_final.columns]
colonnes_absentes = [c for c in colonnes_voulues if c not in df_final.columns]

print("\n✅ Colonnes disponibles :", colonnes_dispo)
print("❌ Colonnes absentes    :", colonnes_absentes)

df_final = df_final[colonnes_dispo]

# =========================================================
# 7. VALEURS MANQUANTES
# =========================================================

print("\n=== VALEURS MANQUANTES ===")
for col in df_final.columns:
    n = df_final[col].isna().sum()
    if n > 0:
        print(f"  {col:40s} : {n} NaN sur {len(df_final)}")

# =========================================================
# 8. NETTOYAGE FINAL POUR RÉGRESSION
# =========================================================

# 1. Variable dépendante → obligatoire
df_final = df_final.dropna(subset=["Evictions_RCLALQ_2023"])

# 2. Retirer les valeurs absurdes (0 créés artificiellement)
cols_cles = [
    "revenu_median_2021",
    "loyer_median_2021",
    "densite_2021"
]
df_final = df_final[(df_final[cols_cles] != 0).all(axis=1)]

# 3. Remplir certaines variables problématiques
df_final["Permis_Renovation"] = df_final["Permis_Renovation"].fillna(0)
df_final["Evictions_Media_Count"] = df_final["Evictions_Media_Count"].fillna(0)

# =========================================================
# 9. EXPORT
# =========================================================

df_final.to_csv("dataset_arrondissement_FINAL_REGRESSION.csv", index=False)

print("\n✅ Dataset FINAL prêt pour régression")
print(df_final.to_string())