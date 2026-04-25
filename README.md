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