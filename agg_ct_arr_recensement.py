import pandas as pd
import geopandas as gpd

# =========================================================
# 0. SPATIAL JOIN : CTUID → ARRONDISSEMENT
# =========================================================

gdf_arr = gpd.read_file("arrondissements_mtl.geojson")
gdf_ct  = gpd.read_file("ct2021_qc.geojson")

gdf_ct_mtl = gdf_ct[gdf_ct['CTUID'].str.startswith('462')].copy()
gdf_arr    = gdf_arr.to_crs("EPSG:3347")
gdf_ct_mtl = gdf_ct_mtl.to_crs("EPSG:3347")

gdf_ct_centroids = gdf_ct_mtl.copy()
gdf_ct_centroids['geometry'] = gdf_ct_centroids.geometry.centroid

ct_with_arr = gpd.sjoin(
    gdf_ct_centroids[['CTUID', 'geometry']],
    gdf_arr[['NOM', 'geometry']],
    how='left', predicate='within'
)

correspondance = ct_with_arr[['CTUID', 'NOM']].rename(
    columns={'NOM': 'arrondissement'}
).drop_duplicates('CTUID')

print(f"CT avec arrondissement : {correspondance['arrondissement'].notna().sum()}")
print(f"CT sans arrondissement : {correspondance['arrondissement'].isna().sum()}")

# =========================================================
# 1. CHARGEMENT
# =========================================================

ct_2016 = pd.read_csv("recensement2016_data.csv", encoding="latin1")
ct_2021 = pd.read_csv("recensement2021_data.csv", encoding="latin1")

# Enlever ligne totale RMR
ct_2016 = ct_2016[ct_2016['COL3'] != 0.0].copy()
ct_2021 = ct_2021[ct_2021['COL3'] != 0.0].copy()
print(f"2016 : {len(ct_2016)} CT | 2021 : {len(ct_2021)} CT")

# =========================================================
# 2. CTUID + JOINTURE ARRONDISSEMENT
# =========================================================

ct_2016['CTUID'] = ct_2016['COL3'].apply(lambda x: f"462{x:07.2f}")
ct_2021['CTUID'] = ct_2021['COL3'].apply(lambda x: f"462{x:07.2f}")

ct_2016 = ct_2016.merge(correspondance, on='CTUID', how='left')
ct_2021 = ct_2021.merge(correspondance, on='CTUID', how='left')

print(f"2016 - CT avec arrondissement : {ct_2016['arrondissement'].notna().sum()}")
print(f"2021 - CT avec arrondissement : {ct_2021['arrondissement'].notna().sum()}")

# =========================================================
# 3. CALCULER LES % AU NIVEAU CT AVANT AGRÉGATION
# =========================================================

# ── 2021 ──────────────────────────────────────────────────
# COL25 = Propriétaire (nombre brut)
# COL26 = Locataire    (nombre brut)
# COL4  = Population totale
# COL19 = Immigrants récents 2016-2021 (nombre brut)
# COL22 = Immigrants total              (nombre brut)

ct_2021['menages_total'] = ct_2021['COL25'] + ct_2021['COL26']

ct_2021['pct_locataires_2021'] = (
    ct_2021['COL26'] / ct_2021['menages_total'] * 100
).clip(0, 100)

ct_2021['pct_proprietaires_2021'] = (
    ct_2021['COL25'] / ct_2021['menages_total'] * 100
).clip(0, 100)

ct_2021['pct_immigrants_rec_2021'] = (
    ct_2021['COL19'] / ct_2021['COL4'] * 100
).clip(0, 100)

# ── 2016 ──────────────────────────────────────────────────
# COL15 = Propriétaire (nombre brut)
# COL16 = Locataire    (nombre brut)
# COL4  = Population totale
# COL28 = Immigrants récents 2011-2016 (nombre brut)
# COL30 = Immigrants total              (nombre brut)

ct_2016['menages_total'] = ct_2016['COL15'] + ct_2016['COL16']

ct_2016['pct_locataires_2016'] = (
    ct_2016['COL16'] / ct_2016['menages_total'] * 100
).clip(0, 100)

ct_2016['pct_proprietaires_2016'] = (
    ct_2016['COL15'] / ct_2016['menages_total'] * 100
).clip(0, 100)

ct_2016['pct_immigrants_rec_2016'] = (
    ct_2016['COL28'] / ct_2016['COL4'] * 100
).clip(0, 100)

# Vérification
print("\n=== VÉRIFICATION % CALCULÉS (doit être entre 0 et 100) ===")
print(ct_2021[['CTUID',
               'pct_locataires_2021',
               'pct_proprietaires_2021',
               'pct_immigrants_rec_2021']].head(5).to_string())

# =========================================================
# 4. AGRÉGATION 2016 (CT → ARRONDISSEMENT)
# =========================================================
# COL4  = Population
# COL6  = Densité
# COL13 = Revenu médian 2015
# COL14 = Revenu après impôt médian 2015
# COL19 = % locataires 30%+ (déjà un %)
# COL20 = Loyer médian locataires ($)
# COL21 = Loyer moyen locataires ($)
# COL22 = Réparations majeures (nombre brut)
# COL23 = Valeur médiane logements ($)
# COL24 = Fréquence faible revenu MFR-ApI (%)
# COL25 = Faible revenu 18-64 ans (%)
# COL27 = Âge moyen

agg_2016 = ct_2016.groupby("arrondissement").agg(
    population_2016          = ("COL4",                   "sum"),
    densite_2016             = ("COL6",                   "mean"),
    age_moyen_2016           = ("COL27",                  "mean"),
    revenu_median_2016       = ("COL13",                  "mean"),
    revenu_apres_impot_2016  = ("COL14",                  "mean"),
    loyer_median_2016        = ("COL20",                  "mean"),
    loyer_moyen_2016         = ("COL21",                  "mean"),
    valeur_logement_2016     = ("COL23",                  "mean"),
    faible_revenu_pct_2016   = ("COL24",                  "mean"),
    pct_loc_30plus_2016      = ("COL19",                  "mean"),
    pct_locataires_2016      = ("pct_locataires_2016",    "mean"),
    pct_proprietaires_2016   = ("pct_proprietaires_2016", "mean"),
    pct_immigrants_rec_2016  = ("pct_immigrants_rec_2016","mean"),
).reset_index()

print(f"\nArrondissements 2016 agrégés : {len(agg_2016)}")

# =========================================================
# 5. AGRÉGATION 2021 (CT → ARRONDISSEMENT)
# =========================================================
# COL4  = Population
# COL6  = Densité
# COL7  = Âge moyen
# COL14 = Revenu médian 2019
# COL15 = Revenu après impôt médian 2019
# COL16 = Fréquence faible revenu MFR-ApI (%)
# COL17 = Faible revenu 18-64 ans (%)
# COL29 = % locataires 30%+ (déjà un %)
# COL30 = Loyer médian locataires ($)
# COL31 = Loyer moyen locataires ($)
# COL32 = Réparations majeures (nombre brut)
# COL33 = Valeur médiane logements ($)

agg_2021 = ct_2021.groupby("arrondissement").agg(
    population_2021          = ("COL4",                    "sum"),
    densite_2021             = ("COL6",                    "mean"),
    age_moyen_2021           = ("COL7",                    "mean"),
    revenu_median_2021       = ("COL14",                   "mean"),
    revenu_apres_impot_2021  = ("COL15",                   "mean"),
    loyer_median_2021        = ("COL30",                   "mean"),
    loyer_moyen_2021         = ("COL31",                   "mean"),
    valeur_logement_2021     = ("COL33",                   "mean"),
    faible_revenu_pct_2021   = ("COL16",                   "mean"),
    pct_loc_30plus_2021      = ("COL29",                   "mean"),
    pct_locataires_2021      = ("pct_locataires_2021",     "mean"),
    pct_proprietaires_2021   = ("pct_proprietaires_2021",  "mean"),
    pct_immigrants_rec_2021  = ("pct_immigrants_rec_2021", "mean"),
).reset_index()

print(f"Arrondissements 2021 agrégés : {len(agg_2021)}")

# =========================================================
# 6. MERGE 2016 + 2021
# =========================================================
ct_panel = agg_2016.merge(agg_2021, on="arrondissement", how="inner")

# Arrondissement officiels de MTL
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

ct_panel = ct_panel[
    ct_panel["arrondissement"].isin(arrondissements_officiels)
]

print(f"\nArrondissements après filtre officiel : {len(ct_panel)}")
print(ct_panel['arrondissement'].tolist())

# ct_panel = agg_2016.merge(agg_2021, on="arrondissement", how="inner")
# print(f"\nArrondissements après merge : {len(ct_panel)}")
# print(ct_panel['arrondissement'].tolist())

# =========================================================
# 7. VARIABLES DYNAMIQUES
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
ct_panel["Delta_Pct_Locataires"] = (
    ct_panel["pct_locataires_2021"] - ct_panel["pct_locataires_2016"]
)
ct_panel["Delta_Faible_Revenu"] = (
    ct_panel["faible_revenu_pct_2021"] - ct_panel["faible_revenu_pct_2016"]
)
ct_panel["Ratio_Loyer_Revenu_2021"] = (
    ct_panel["loyer_median_2021"] / (ct_panel["revenu_median_2021"] / 12) * 100
)
ct_panel["Ratio_Loyer_Revenu_2016"] = (
    ct_panel["loyer_median_2016"] / (ct_panel["revenu_median_2016"] / 12) * 100
)
ct_panel["Delta_Ratio_Loyer_Revenu"] = (
    ct_panel["Ratio_Loyer_Revenu_2021"] - ct_panel["Ratio_Loyer_Revenu_2016"]
)

# =========================================================
# 8. EXPORT
# =========================================================

ct_panel.to_csv("ct_arrondissement_features.csv", index=False)
print("\n✅ Recensement agrégé ARRONDISSEMENT prêt")
print(ct_panel[['arrondissement',
                'pct_locataires_2021',
                'pct_immigrants_rec_2021',
                'loyer_median_2021',
                'Augmentation_Loyer_16_21',
                'Ratio_Loyer_Revenu_2021']].to_string())