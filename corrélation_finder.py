import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("dataset_arrondissement_FINAL_REGRESSION.csv")

# Garder seulement les arrondissements avec données RCLALQ
df_reg = df.dropna(subset=["Evictions_RCLALQ_2023"])

vars_reg = [
    "Evictions_RCLALQ_2023",
    "Airbnb_Count",
    "Augmentation_Loyer_16_21",
    "pct_locataires_2021",
    "revenu_median_2021",
    "pct_immigrants_rec_2021",
    "densite_2021"
]

# Matrice de corrélation
corr = df_reg[vars_reg].corr()
print("=== CORRÉLATIONS AVEC ÉVICTIONS ===")
print(corr["Evictions_RCLALQ_2023"].sort_values(ascending=False))

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Corrélations entre variables")
plt.tight_layout()
plt.savefig("correlations.png")
plt.show()

# Scatterplots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for i, var in enumerate(vars_reg[1:]):
    axes[i].scatter(df_reg[var], df_reg["Evictions_RCLALQ_2023"])
    axes[i].set_xlabel(var)
    axes[i].set_ylabel("Evictions_RCLALQ_2023")
    # Ajouter noms arrondissements
    for _, row in df_reg.iterrows():
        axes[i].annotate(
            row["NOM"][:10],
            (row[var], row["Evictions_RCLALQ_2023"]),
            fontsize=7
        )
plt.tight_layout()
plt.savefig("scatterplots.png")
plt.show()