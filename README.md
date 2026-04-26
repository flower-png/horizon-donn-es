# Ordre de travail à faire
|Fait|Étape | Quoi faire|
|----|------|-----------|
| ✅ | 1    |Télécharger Inside Airbnb (archives 2018-2024)|
| ✅ | 2    |Extraire loyers médians recensement 2016 + 2021 par CT|
| ✅ | 3    |Télécharger pression immobilière et permis de construction|
|    | 4    |Construire le panel de données par census tract + annéeRégression spatiale dans GeoDa +    régression temporelle| 

# Plutôt qu'une seule régression, pensez à 3 analyses complémentaires :
```
1. PRESSION DU MARCHÉ     →    2. MÉCANISMES D'ÉVICTION    →    3. EFFETS
   (causes)                       (processus)                     (résultats)

Airbnb ↑                         Renovictions                     Évictions ↑
Prix immobilier ↑                                                  Déplacement
Loyer ↑                                                          Perte logements
Salaire stagnant                                                   abordables
```

# Par variable — quoi faire avec les données
## 💰 Loyers (2016, 2021, 2023)

Source : Recensement StatCan 2016 + 2021\
Quoi faire : Calculer le % d'augmentation par census tract \
Analyse : Carte choroplèthe + corrélation avec densité Airbnb

## 📈 Airbnb par année

Source : Inside Airbnb (archives disponibles)\
Quoi faire : Compter les listings Entire home/apt par census tract par année → courbe de croissance\
Analyse : Régression temporelle — est-ce que l'augmentation Airbnb précède l'augmentation des évictions ?

## 💼 Revenus vs loyers

Source : Recensement StatCan\
Quoi faire : Calculer le ratio loyer/revenu médian par census tract en 2016 et 2021\
Analyse : Identifier les zones où l'écart se creuse le plus


# Structure de regression suggéré
**Variable dépendante** :
```
Évictions_2023 (média) échelle arrondissement
```

**Variables indépendantes** :
```
Airbnb_Count_Entire           (pression directe) mettre en échelle arrondissement
Augmentation_Loyer_16_21      (pression marché) à calculer et mettre en échelle arrondissement
Augmentation_Valeur_16_21 (%) (pression immobilière) à calculer et mettre en échelle arrondissement
Ratio_Loyer_Revenu            (vulnérabilité) à calculer prendre celui de de 2021? et mettre en échelle arrondissement
Permis_Renovation             (renovictions) 
```

**Variables de contrôle** :
```
% Locataires prendre celui de 2021? et mettre en échelle arrondissement
Revenu_Median prendre celui de 2021? et mettre en échelle arrondissement
% Immigrants_Recents à calculer et mettre en échelle arrondissement
Densite_Population prendre celui de 2021? et mettre en échelle arrondissement
```

# Documentation des variables du recensement
## Tableau de correspondance 2016 — 2021
 
| Données | 2016 | 2021 |
|--------|------|------|
| **Logement** | | |
| Occupation : Propriétaire | v3886 | v4064 |
| Occupation : Locataire | v3887 | v4065 |
| **Inabordabilité** | | |
| 30% ou plus du revenu consacré au logement (tous) | v3937 | v4116 |
| % propriétaires consacrant 30%+ au logement | v3941 | v4133 |
| % locataires consacrant 30%+ au logement | v3948 | v4141 |
| Frais de logement mensuels MÉDIANS locataires ($) | v3949 | v4143 |
| Frais de logement mensuels MOYENS locataires ($) | v3950 | v4144 |
| Réparations majeures requises | v3921 | v4100 |
| Valeur médiane des logements ($) | v3944 | v4137 |
| **Revenu** | | |
| Revenu total médian individuel ($) | v1868 | v293 (2019) |
| Revenu après impôt médian individuel ($) | v1870 | v295 (2019) |
| Fréquence du faible revenu MFR-ApI (%) | v2023 | v317 |
| Faible revenu 18 à 64 ans (%) | v2026 | v320 |
| Faible revenu 65 ans et plus (%) | v2027 | v321 |
| **Population** | | |
| Population | v1 | v1 |
| Variation population (%) | v3 | v3 |
| Densité de population (km²) | v6 | v6 |
| Âge moyen | v34 | v39 |
| % 15 à 64 ans | v37 | v36 |
| % 65 ans et plus | v38 | v37 |
| **Habitation** | | |
| Appartement ou plain-pied dans un duplex | v110 | v111 |
| Appartement immeuble moins de 5 étages | v111 | v112 |
| Appartement immeuble 5 étages ou plus | v106 | v113 |
| Taille moyenne des ménages | v121 | v122 |
| **Immigration** | | |
| Immigrants récents | v3290 | v4163 |
| Résidents non permanents | v3291 | v4164 |
| Non-immigrants | v3282 | v4155 |
| Immigrants (total) | v3283 | v4156 |
| Réfugiés | v3428 | v4301 |
| Immigrants parrainés par la famille | v3427 | v4300 |

## Explication des variables
 
### 🏠 Logement
 
#### Mode d'occupation
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3886 | v4064 | Nombre de ménages propriétaires |
| v3887 | v4065 | Nombre de ménages locataires |
 
Indique la proportion de locataires par secteur de recensement — les secteurs à forte proportion de locataires sont plus vulnérables aux évictions et à la pression du marché Airbnb.
 
#### Inabordabilité
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3937 | v4116 | 30%+ du revenu consacré au logement (tous ménages) |
| v3941 | v4133 | % propriétaires consacrant 30%+ au logement |
| v3948 | v4141 | % locataires consacrant 30%+ au logement ⭐ priorité haute |
 
Le seuil de 30% est la mesure standard d'inabordabilité du logement au Canada. Un ménage qui dépasse ce seuil est considéré en situation de stress financier lié au logement. **v3948/v4141** est votre indicateur le plus important car il cible directement les locataires.
 
#### Loyers
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3949 | v4143 | Frais de logement mensuels MÉDIANS locataires ($) ⭐ |
| v3950 | v4144 | Frais de logement mensuels MOYENS locataires ($) |
 
La médiane est préférable à la moyenne car elle est moins affectée par les valeurs extrêmes. 

#### État du logement
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3921 | v4100 | Réparations majeures requises |
 
Indicateur de dégradation du parc locatif. Un nombre élevé de logements nécessitant des réparations majeures peut signaler des situations de renoviction — propriétaires qui utilisent les travaux comme prétexte pour évincer les locataires.
 
#### Valeur immobilière
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3944 | v4137 | Valeur médiane des logements ($) |
 
Mesure la pression du marché immobilier. Une forte hausse de la valeur des logements entre 2016 et 2021 indique une gentrification en cours, ce qui est corrélé avec une augmentation des évictions.
 
---
 
### 💰 Revenu
 
#### Revenu médian individuel
 
> ⚠️ **Note méthodologique importante :** Les revenus 2020 sont biaisés par les prestations COVID-19 (PCU). Utilisez **v293/v295** (revenus 2019, pré-COVID) pour comparer avec 2016. Mentionnez cette décision dans votre analyse.
 
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v1868 | v293 | Revenu total médian individuel ($) — utiliser 2019 |
| v1870 | v295 | Revenu après impôt médian individuel ($) — utiliser 2019 |

#### Faible revenu
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v2023 | v317 | Fréquence du faible revenu MFR-ApI (%) |
| v2026 | v320 | Faible revenu 18 à 64 ans (%) |
| v2027 | v321 | Faible revenu 65 ans et plus (%) |
 
La Mesure de faible revenu après impôt (MFR-ApI) identifie les ménages dont le revenu est nettement inférieur à la médiane canadienne. Les secteurs à fort taux de faible revenu sont plus vulnérables aux évictions car les résidents ont moins de ressources pour se défendre au TAL ou se reloger.
 
---
 
### 👥 Démographie
 
#### Population
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v1 | v1 | Population totale du secteur |
| v3 | v3 | Variation de la population (%) |
| v6 | v6 | Densité de population (hab/km²) |
 
La variation de population permet d'identifier les secteurs en forte croissance (gentrification possible) ou en déclin (déplacement de population).
 
#### Âge
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v34 | v39 | Âge moyen de la population |
| v37 | v36 | % population 15 à 64 ans |
| v38 | v37 | % population 65 ans et plus |
 
Les personnes âgées sont particulièrement vulnérables aux évictions car elles ont souvent des revenus fixes (retraite) qui n'augmentent pas au même rythme que les loyers.
 
#### Type de logement
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v110 | v111 | Appartement ou plain-pied dans un duplex |
| v111 | v112 | Appartement dans un immeuble de moins de 5 étages |
| v106 | v113 | Appartement dans un immeuble de 5 étages ou plus |
| v121 | v122 | Taille moyenne des ménages privés |
 
Le duplex et l'immeuble de moins de 5 étages sont les types de logement locatif les plus communs à Montréal. Une diminution de ces types entre 2016 et 2021 peut indiquer des conversions vers Airbnb ou des condos.
 
---
 
### 🌍 Immigration
 
#### Statut d'immigrant
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3290 | v4163 | Immigrants récents (arrivés dans les 5 dernières années) ⭐ |
| v3291 | v4164 | Résidents non permanents |
| v3282 | v4155 | Non-immigrants |
| v3283 | v4156 | Immigrants (total) |
 
> ⭐ **Variable clé :** Les immigrants récents (v3290/v4163) sont particulièrement vulnérables aux évictions car ils sont :
> - Moins bien informés de leurs droits comme locataires au Québec
> - Souvent dans des logements précaires ou informels
> - Moins susceptibles de contester une éviction au TAL
> - Plus susceptibles d'accepter des conditions de logement défavorables
 
#### Catégorie d'admission
| Variable 2016 | Variable 2021 | Description |
|---|---|---|
| v3428 | v4301 | Réfugiés |
| v3427 | v4300 | Immigrants parrainés par la famille |
 
Les réfugiés sont la catégorie la plus vulnérable — ils arrivent souvent sans réseau de soutien solide et avec des ressources financières limitées, ce qui les rend particulièrement exposés aux pratiques d'éviction abusives.
 
---
# Résultat
## Régression

🟢 Résultats globaux
```
R² = 0.34         → densité explique 34% des évictions ✅
R² ajusté = 0.28  → positif et stable ✅
F-statistic p = 0.038 → SIGNIFICATIF (< 0.05) ✅ première fois !
```

📊 Variable significative
```
densite_2021  coef = 0.033  p = 0.038  ✅ SIGNIFICATIF
Interprétation concrète :
Chaque augmentation de 1000 personnes/km²
= environ 33 évictions supplémentaires par année
```

🟢 Diagnostics tous bons
```
Multicolinéarité   = 6.6   ✅ excellent (était 22.9 avant)
Jarque-Bera p      = 0.10  ✅ erreurs normales
Breusch-Pagan p    = 0.38  ✅ pas d'hétéroscédasticité
```

⚠️ Limites à mentionner dans votre travail
1. N = 13 → petit échantillon, résultats à interpréter avec prudence
2. R² = 0.34 → 66% des évictions sont expliquées par d'autres facteurs
               non capturés dans ce modèle
3. La densité est un proxy — elle capture indirectement
   la pression du marché locatif, la concentration Airbnb,
   et la vulnérabilité des locataires
4. Airbnb n'est pas significatif à cette échelle
   → lien indirect médié par la densité urbaine

💡 Ce que vous pouvez conclure
```
"La densité de population est le seul prédicteur
significatif des évictions à l'échelle des
arrondissements de Montréal (β = 0.033, p = 0.038).

Les arrondissements plus denses — comme Rosemont,
Le Plateau et Villeray — concentrent davantage
d'évictions, reflétant une pression plus intense
sur le marché locatif.

Bien qu'Airbnb soit souvent associé aux évictions
dans la littérature, son effet direct n'est pas
détectable à cette échelle d'analyse, suggérant
que son impact transite par d'autres mécanismes
comme la hausse des loyers et la densification."
```

## Stats 
Analyse des statistiques descriptives
🏠 Logement — Ce qui ressort
```
Loyer médian 2016 : 786 $  →  Loyer médian 2021 : 906 $
Augmentation moyenne : 15% sur 5 ans
→ Certains arrondissements jusqu'à +28% ⚠️
% locataires moyen : 65%  (min 36%, max 73%)
→ Montréal est majoritairement locataire
→ Population très exposée aux évictions
```
💰 Revenu — Problème important
```
Augmentation revenu : 17% (0.17)
Augmentation loyer  : 15%
→ Les loyers augmentent presque autant que les revenus
→ Mais le revenu médian reste bas : 34 378 $
→ Loyer moyen = 906 $ = ~10 872 $/an = 32% du revenu médian
→ Juste au seuil d'inabordabilité (30%)
```
🏡 Airbnb — Très variable
```
Moyenne : 506 listings    
Médiane : 216 listings    ← écart énorme avec la moyenne
Maximum : 2611 listings   ← probablement Ville-Marie ou Plateau
Écart-type : 740          ← très grande disparité entre arrondissements
La médiane beaucoup plus basse que la moyenne indique que quelques arrondissements concentrent la majorité des Airbnb.
```
📉 Variation ratio loyer/revenu
```
Moyenne : -0.56  ← le ratio a diminué en moyenne
→ Contre-intuitif mais s'explique par les transferts COVID
   qui ont gonflé les revenus 2020 artificiellement
```
✅ Ce que vous pouvez dire dans votre travail
```
"Entre 2016 et 2021, le loyer médian a augmenté 
de 15% dans les arrondissements montréalais étudiés,
tandis que le revenu médian n'a progressé que de 17%.

Avec un loyer médian de 906$ représentant environ 
32% du revenu médian mensuel, les locataires 
montréalais se situent juste au seuil critique 
d'inabordabilité défini par la SCHL (30%).

La forte disparité dans la distribution des 
listings Airbnb (médiane = 216, maximum = 2611) 
suggère une concentration spatiale de la pression
touristique dans quelques arrondissements centraux."
```

💡 Statistiques les plus parlantes pour votre présentation
|Statistique|Valeur|Impact|
|-----------|------|------|
|Hausse loyer max|+28% |Très parlant% |
|locataires moyen| 65% |Vulnérabilité|
|Loyer/revenu| 32% |Inabordabilité|
|Max Airbnb| 2611 |Concentration|
|Max évictions| 591 | Rosemont|


---