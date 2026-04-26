import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("dataset_arrondissement_FINAL_REGRESSION.csv")

# =========================================================
# STATISTIQUES DESCRIPTIVES — FACTEURS D'ÉVICTION
# =========================================================

# Variables à analyser avec leurs labels lisibles
variables = {
    "Augmentation_Loyer_16_21"   : "Augmentation du loyer 2016-2021 (%)",
    "Augmentation_Valeur_16_21"  : "Augmentation valeur immobilière 2016-2021 (%)",
    "Augmentation_Revenu_16_21"  : "Augmentation du revenu 2016-2021 (%)",
    "Delta_Ratio_Loyer_Revenu"   : "Variation ratio loyer/revenu",
    "Airbnb_Count"               : "Nombre de listings Airbnb",
    "pct_locataires_2021"        : "% locataires (2021)",
    "revenu_median_2021"         : "Revenu médian 2021 ($)",
    "loyer_median_2021"          : "Loyer médian 2021 ($)",
    "loyer_median_2016"          : "Loyer médian 2016 ($)",
    "densite_2021"               : "Densité population (hab/km²)",
    "pct_immigrants_rec_2021"    : "% immigrants récents (2021)",
    "faible_revenu_pct_2021"     : "% faible revenu (2021)",
    "Evictions_RCLALQ_2023"      : "Évictions RCLALQ 2023",
}

# =========================================================
# 1. TABLEAU STATISTIQUES DESCRIPTIVES
# =========================================================

rows = []
for col, label in variables.items():
    if col in df.columns:
        serie = df[col].dropna()
        # Convertir augmentations en % lisibles
        if "Augmentation" in col and col != "Augmentation_Revenu_16_21":
            serie = serie * 100
        rows.append({
            "Variable"  : label,
            "N"         : int(serie.count()),
            "Moyenne"   : round(serie.mean(), 2),
            "Médiane"   : round(serie.median(), 2),
            "Min"       : round(serie.min(), 2),
            "Max"       : round(serie.max(), 2),
            "Écart-type": round(serie.std(), 2),
        })

stats_df = pd.DataFrame(rows)
print(stats_df.to_string(index=False))
stats_df.to_csv("statistiques_descriptives.csv", index=False)

# =========================================================
# 2. TABLEAU PAR ARRONDISSEMENT — FACTEURS CLÉS
# =========================================================

cols_affichage = {
    "NOM"                        : "Arrondissement",
    "Evictions_RCLALQ_2023"      : "Évictions 2023",
    "Airbnb_Count"               : "Airbnb",
    "loyer_median_2016"          : "Loyer 2016 ($)",
    "loyer_median_2021"          : "Loyer 2021 ($)",
    "Augmentation_Loyer_16_21"   : "Hausse loyer (%)",
    "revenu_median_2021"         : "Revenu médian ($)",
    "pct_locataires_2021"        : "% Locataires",
    "densite_2021"               : "Densité",
}

cols_dispo = {k: v for k, v in cols_affichage.items() if k in df.columns}
tableau = df[list(cols_dispo.keys())].rename(columns=cols_dispo).copy()

# Arrondir hausse loyer en %
if "Hausse loyer (%)" in tableau.columns:
    tableau["Hausse loyer (%)"] = (tableau["Hausse loyer (%)"] * 100).round(1)

# Trier par évictions décroissant
tableau = tableau.sort_values("Évictions 2023", ascending=False)

print("\n=== TABLEAU PAR ARRONDISSEMENT ===")
print(tableau.to_string(index=False))
tableau.to_csv("tableau_arrondissements.csv", index=False)

# =========================================================
# 3. GRAPHIQUES
# =========================================================

fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle("Facteurs potentiels d'éviction — Montréal 2023", fontsize=14)

df_plot = df.dropna(subset=["Evictions_RCLALQ_2023"]).copy()
df_plot["Hausse_Loyer_pct"] = df_plot["Augmentation_Loyer_16_21"] * 100

plots = [
    ("densite_2021",         "Densité (hab/km²)",        "Densité vs Évictions"),
    ("Airbnb_Count",         "Nombre Airbnb",             "Airbnb vs Évictions"),
    ("Hausse_Loyer_pct",     "Hausse loyer 2016-21 (%)",  "Hausse loyer vs Évictions"),
    ("revenu_median_2021",   "Revenu médian ($)",         "Revenu vs Évictions"),
    ("pct_locataires_2021",  "% Locataires",              "% Locataires vs Évictions"),
    ("faible_revenu_pct_2021","% Faible revenu",          "Faible revenu vs Évictions"),
]

for ax, (xvar, xlabel, titre) in zip(axes.flatten(), plots):
    if xvar not in df_plot.columns:
        continue
    x = df_plot[xvar]
    y = df_plot["Evictions_RCLALQ_2023"]
    ax.scatter(x, y, color="steelblue", s=80, zorder=3)

    # Ligne de tendance
    mask = x.notna() & y.notna()
    if mask.sum() > 2:
        z = np.polyfit(x[mask], y[mask], 1)
        p = np.poly1d(z)
        xline = np.linspace(x[mask].min(), x[mask].max(), 100)
        ax.plot(xline, p(xline), "r--", alpha=0.7)

    # Étiquettes arrondissements
    for _, row in df_plot.iterrows():
        if pd.notna(row[xvar]):
            ax.annotate(
                row["NOM"][:12],
                (row[xvar], row["Evictions_RCLALQ_2023"]),
                fontsize=7, alpha=0.8
            )

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Évictions RCLALQ 2023")
    ax.set_title(titre)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("facteurs_eviction.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n✅ Graphiques sauvegardés : facteurs_eviction.png")