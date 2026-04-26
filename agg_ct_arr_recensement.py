import pandas as pd
import geopandas as gpd

# =========================================================
# 0. SPATIAL JOIN : CTUID → ARRONDISSEMENT
# =========================================================

gdf_arr = gpd.read_file("arrondissements_mtl.geojson")
gdf_ct  = gpd.read_file("ct2021_qc.geojson")

# Filtrer Montréal seulement
gdf_ct_mtl = gdf_ct[gdf_ct['CTUID'].str.startswith('462')].copy()
print(f"Census tracts Montréal : {len(gdf_ct_mtl)}")

# Harmoniser les deux en EPSG:3347 (projection, pas géographique)
gdf_arr    = gdf_arr.to_crs("EPSG:3347")
gdf_ct_mtl = gdf_ct_mtl.to_crs("EPSG:3347")

# Calculer centroïdes EN PROJECTION (résultats corrects)
gdf_ct_centroids = gdf_ct_mtl.copy()
gdf_ct_centroids['geometry'] = gdf_ct_centroids.geometry.centroid

ct_with_arr = gpd.sjoin(
    gdf_ct_centroids[['CTUID', 'geometry']],
    gdf_arr[['NOM', 'geometry']],
    how='left',
    predicate='within'
)

correspondance = ct_with_arr[['CTUID', 'NOM']].rename(
    columns={'NOM': 'arrondissement'}
).drop_duplicates('CTUID')

print(f"CT avec arrondissement : {correspondance['arrondissement'].notna().sum()}")
print(f"CT sans arrondissement : {correspondance['arrondissement'].isna().sum()}")

# =========================================================
# 1. CHARGEMENT RECENSEMENT
# =========================================================

ct_2016 = pd.read_csv("recensement2016_data.csv", encoding="latin1")
ct_2021 = pd.read_csv("recensement2021_data.csv", encoding="latin1")

# Enlever la ligne totale RMR (SR = 0.00)
ct_2016 = ct_2016[ct_2016['COL3'] != 0.0].copy()
ct_2021 = ct_2021[ct_2021['COL3'] != 0.0].copy()
print(f"\n2016 : {len(ct_2016)} census tracts")
print(f"2021 : {len(ct_2021)} census tracts")

# =========================================================
# 2. CRÉER CTUID ET JOINDRE L'ARRONDISSEMENT
# =========================================================

ct_2016['CTUID'] = ct_2016['COL3'].apply(lambda x: f"462{x:07.2f}")
ct_2021['CTUID'] = ct_2021['COL3'].apply(lambda x: f"462{x:07.2f}")

# Diagnostic format (maintenant CTUID existe)
print("\nExemples CTUID CHASS  :", ct_2016['CTUID'].head(5).tolist())
print("Exemples CTUID GeoJSON:", correspondance['CTUID'].head(5).tolist())

# Joindre la table de correspondance
ct_2016 = ct_2016.merge(correspondance, on='CTUID', how='left')
ct_2021 = ct_2021.merge(correspondance, on='CTUID', how='left')

print(f"\n2016 - CT avec arrondissement : {ct_2016['arrondissement'].notna().sum()}")
print(f"2021 - CT avec arrondissement : {ct_2021['arrondissement'].notna().sum()}")
print("\nArrondissements 2016 :")
print(ct_2016['arrondissement'].value_counts())

# =========================================================
# 3. AGRÉGATION 2016 (CT → ARRONDISSEMENT)
# =========================================================

agg_2016 = ct_2016.groupby("arrondissement").agg(
    population_2016        = ("COL4",  "sum"),
    densite_2016           = ("COL6",  "mean"),
    revenu_median_2016     = ("COL17", "mean"),
    revenu_apres_impot_2016= ("COL18", "mean"),
    pct_locataires_2016    = ("COL26", "mean"),
    pct_proprietaires_2016 = ("COL25", "mean"),
    ratio_loyer_revenu_2016= ("COL27", "mean"),
    loyer_median_2016      = ("COL30", "mean"),
    valeur_logement_2016   = ("COL33", "mean"),
    immigrants_recents_2016= ("COL19", "mean")
).reset_index()

print(f"\nArrondissements 2016 agrégés : {len(agg_2016)}")

# =========================================================
# 4. AGRÉGATION 2021 (CT → ARRONDISSEMENT)
# =========================================================

agg_2021 = ct_2021.groupby("arrondissement").agg(
    population_2021        = ("COL4",  "sum"),
    densite_2021           = ("COL6",  "mean"),
    revenu_median_2021     = ("COL14", "mean"),
    revenu_apres_impot_2021= ("COL15", "mean"),
    pct_locataires_2021    = ("COL26", "mean"),
    pct_proprietaires_2021 = ("COL25", "mean"),
    ratio_loyer_revenu_2021= ("COL27", "mean"),
    loyer_median_2021      = ("COL30", "mean"),
    valeur_logement_2021   = ("COL33", "mean"),
    immigrants_recents_2021= ("COL19", "mean")
).reset_index()

print(f"Arrondissements 2021 agrégés : {len(agg_2021)}")

# =========================================================
# 5. MERGE 2016 + 2021
# =========================================================

ct_panel = agg_2016.merge(agg_2021, on="arrondissement", how="inner")
print(f"\nArrondissements après merge : {len(ct_panel)}")
print(ct_panel['arrondissement'].tolist())

# =========================================================
# 6. VARIABLES DYNAMIQUES
# =========================================================

ct_panel["croissance_pop_16_21"] = (
    (ct_panel["population_2021"] - ct_panel["population_2016"])
    / ct_panel["population_2016"]
)
ct_panel["Augmentation_Loyer_16_21"] = (
    (ct_panel["loyer_median_2021"] - ct_panel["loyer_median_2016"])
    / ct_panel["loyer_median_2016"]
)
ct_panel["Augmentation_Valeur_16_21"] = (
    (ct_panel["valeur_logement_2021"] - ct_panel["valeur_logement_2016"])
    / ct_panel["valeur_logement_2016"]
)
ct_panel["Augmentation_Revenu_16_21"] = (
    (ct_panel["revenu_median_2021"] - ct_panel["revenu_median_2016"])
    / ct_panel["revenu_median_2016"]
)
ct_panel["Delta_Ratio_Loyer_Revenu"] = (
    ct_panel["ratio_loyer_revenu_2021"] - ct_panel["ratio_loyer_revenu_2016"]
)

# =========================================================
# 7. VARIABLES FINALES
# =========================================================

df_ct_final = ct_panel[[
    "arrondissement",
    "Augmentation_Loyer_16_21",
    "Augmentation_Valeur_16_21",
    "Delta_Ratio_Loyer_Revenu",
    "pct_locataires_2021",
    "revenu_median_2021",
    "immigrants_recents_2021",
    "densite_2021",
    "croissance_pop_16_21"
]]

# =========================================================
# 8. EXPORT
# =========================================================

df_ct_final.to_csv("ct_arrondissement_features.csv", index=False)
print("\n✅ Recensement agrégé ARRONDISSEMENT prêt pour régression")
print(df_ct_final)