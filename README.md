# Plutôt qu'une seule régression, pensez à 3 analyses complémentaires :
```
1. PRESSION DU MARCHÉ     →    2. MÉCANISMES D'ÉVICTION    →    3. EFFETS
   (causes)                       (processus)                     (résultats)

Airbnb ↑                         Renovictions                     Évictions ↑
Prix immobilier ↑                Harcèlement TAL                  Déplacement
Loyer ↑                          Rachats corporatifs              Perte logements
Salaire stagnant                 Délais TAL                       abordables
```

# Par variable — quoi faire avec les données
## 💰 Loyers (2016, 2021, 2023)

Source : Recensement StatCan 2016 + 2021, SCHL annuel \
Quoi faire : Calculer le % d'augmentation par census tract \
Analyse : Carte choroplèthe + corrélation avec densité Airbnb

## 📈 Airbnb par année

Source : Inside Airbnb (archives disponibles)\
Quoi faire : Compter les listings Entire home/apt par census tract par année → courbe de croissance\
Analyse : Régression temporelle — est-ce que l'augmentation Airbnb précède l'augmentation des évictions ?

## 🏢 Rachats corporatifs

Source : Rôle foncier Montréal + Registre foncier Québec\
Quoi faire : Identifier les acheteurs non-individuels (compagnies, REITs)\
Analyse : Comparer taux d'éviction dans immeubles corporatifs vs individuels

## 🔨 Logements retirés du marché

Source : Permis Ville de Montréal + changements d'usage\
Quoi faire : Comptabiliser conversions locatif → Airbnb ou condo par quartier\
Analyse : Corrélation avec taux d'inoccupation SCHL

## ⚖️ TAL — délais et harcèlement

Source : Données TAL (accès via demande d'accès à l'information)\
Quoi faire : Délai moyen par type de cause + volume de dossiers par quartier\
Analyse : Est-ce que les délais longs découragent les locataires ?

## 💼 Revenus vs loyers

Source : Recensement StatCan\
Quoi faire : Calculer le ratio loyer/revenu médian par census tract en 2016 et 2021\
Analyse : Identifier les zones où l'écart se creuse le plus


# Structure de regression suggéré
**Variable dépendante** :
```
Évictions_2023 (par census tract)
```

**Variables indépendantes** :
```
Airbnb_Count_Entire          (pression directe)
Augmentation_Loyer_16_21     (pression marché)
Rachats_Corporatifs          (acteurs)
Ratio_Loyer_Revenu           (vulnérabilité)
Permis_Renovation            (renovictions)
Delai_Moyen_TAL              (accès justice)
```

**Variables de contrôle** :
```
% Locataires
Revenu_Median
% Immigrants_Recents
Densite_Population
```

# Ordre de travail recommandé
|Fait|Étape | Quoi faire|
|----|------|-----------|
|    | 1    |Télécharger Inside Airbnb (archives 2018-2024)|
|    | 2    |Extraire loyers médians recensement 2016 + 2021 par CT|
|    | 3    |Demander données TAL par accès à l'information|
|    | 4    |Télécharger rôle foncier Montréal (rachats corporatifs)|
|    | 5    |Construire le panel de données par census tract + année6Régression spatiale dans GeoDa +    régression temporelle| 

# Données rencesement à télécharger
## Logement
### Mode d'occupation (essentiel)
```
v3886 - Propriétaire
v3887 - Locataire
```
### Inabordabilité (très important)
```
v3937 - 30% ou plus du revenu consacré au logement (tous)
v3941 - % propriétaires consacrant 30%+ au logement
v3948 - % locataires consacrant 30%+ au logement  ← priorité haute
```
### Loyers (cœur de votre analyse)
```
v3949 - Frais de logement mensuels MÉDIANS locataires ($)  ← le plus important
v3950 - Frais de logement mensuels MOYENS locataires ($)
```
### État du logement (renovictions)
```
v3921 - Réparations majeures requises  ← lié aux renovictions
```
### Valeur immobilière
```
v3944 - Valeur médiane des logements ($)  ← pression marché
```

## Revenu

### Revenu des ménages (essentiel)
```
v1932 - Revenu total médian des ménages en 2015 ($)        ← le plus important
v1933 - Revenu après impôt médian des ménages en 2015 ($)  ← revenu réel
```
### Faible revenu (vulnérabilité)
```
v2023 - Fréquence du faible revenu MFR-ApI (%)             ← taux pauvreté global
v2026 - 18 à 64 ans (%)                                    ← population active
```
### Revenu individuel
```
v1868 - Revenu total médian en 2015 ($)                    ← revenu individuel
v1870 - Revenu après impôt médian en 2015 ($)              ← revenu net
```

## Démographie
### Population
```
v1  - Population 2016                        ← taille du secteur
v3  - Variation population 2011-2016 (%)     ← croissance/déclin
v6  - Densité de population (km²)            ← urbanité
```

### Âge
```
v34 - Âge moyen                              ← profil démographique
v37 - % 15 à 64 ans                          ← population active
v38 - % 65 ans et plus                       ← personnes âgées vulnérables
```

### Habitation
```
v111 - Appartement immeuble moins 5 étages   ← type dominant à Montréal
v106 - Appartement immeuble 5 étages ou plus ← logement locatif dense
v121 - Taille moyenne des ménages            ← surpeuplement
``` 

### Immigration
```
v3290 - Immigrants arrivés 2011 à 2016        ← immigrants récents = vulnérables
v3291 - Résidents non permanents              ← très vulnérables aux évictions
v3282 - Non-immigrants                        ← population de référence
v3283 - Immigrants (total)                    ← proportion générale
v3428 - Réfugiés                              ← population très vulnérable
v3427 - Immigrants parrainés par la famille   ← revenus souvent plus faibles
```
⚠️ Note importante
v3290 (immigrants 2011-2016) est votre variable clé car ces personnes sont :

Moins bien informées de leurs droits comme locataires
Souvent dans des logements précaires
Moins susceptibles de contester une éviction au TAL

Combinez-la avec v3948 (% locataires consacrant 30%+ au logement) pour créer un indice de vulnérabilité par secteur de recensement.