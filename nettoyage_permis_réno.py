import pandas as pd

# 1. Charger les données
df = pd.read_csv("permis-construction.csv")

# 2. Convertir la date
df["date_emission"] = pd.to_datetime(df["date_emission"], errors="coerce")
df["annee"] = df["date_emission"].dt.year
df = df[(df["annee"] >= 2016) & (df["annee"] <= 2023)]

# 3. Filtre de base
df = df[
    (df["description_type_batiment"] == "Résidentiel") &
    (df["code_type_base_demande"] == "TR")  # Transformation
]

# 4. Nettoyer texte
df["nature_travaux_clean"] = df["nature_travaux"].str.lower()

# 5. MOTS-CLÉS À GARDER (rénovations importantes)
keywords_keep = [
    "logement",
    "agrandissement",
    "ajout",
    "conversion",
    "réaménagement",
    "réfection",
    "division",
    "multi",
    "triplex",
    "duplex"
]

# 6. MOTS-CLÉS À EXCLURE (petits travaux)
keywords_exclude = [
    "patio",
    "balcon",
    "toiture",
    "fenêtre",
    "porte",
    "garage",
    "clôture",
    "cabanon",
    "piscine"
]

# 7. Appliquer filtres texte
mask_keep = df["nature_travaux_clean"].str.contains("|".join(keywords_keep), na=False)
mask_exclude = df["nature_travaux_clean"].str.contains("|".join(keywords_exclude), na=False)

df_filtered = df[mask_keep & ~mask_exclude]

# 8. Agrégation par arrondissement + année
agg = df_filtered.groupby(["arrondissement", "annee"]).agg(
    nb_permis=("id_permis", "count")
).reset_index()

# 9. Sauvegarder
df_filtered.to_csv("permis_filtres.csv", index=False)
agg.to_csv("permis_aggregation_arrondissement.csv", index=False)

print("Fichiers générés :")
print("- permis_filtres.csv")
print("- permis_aggregation_arrondissement.csv")