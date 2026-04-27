import pandas as pd
import matplotlib.pyplot as plt

# Charger ton CSV
df = pd.read_csv("statistiques_descriptives.csv")

# Créer la figure
fig, ax = plt.subplots(figsize=(12, 6))
ax.axis('off')  # enlève les axes

# Créer le tableau
table = ax.table(
    cellText=df.values,
    colLabels=df.columns,
    loc='center',
    cellLoc='center'
)

# Ajuster la taille
table.auto_set_font_size(False)
table.set_fontsize(10)
table.auto_set_column_width(col=list(range(len(df.columns))))
table.scale(1, 1.5)  # (largeur, hauteur)


# Sauvegarder en PNG
plt.savefig("tableau_statistiques.png", bbox_inches='tight', dpi=200)
plt.close()

print("✅ Tableau sauvegardé en image (PNG)")