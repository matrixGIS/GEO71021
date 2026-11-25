# TP3: Séries temporelles

## Notions importantes pour le laboratoire
### Autocorrélation
L'autocorrélation est la corrélation d'une série avec elle-même, décalée dans le temps. La plupart des tests statistiques supposent des observations **indépendantes** (sans autocorrélation). Ne pas respecter cette prémisse peut biaiser les résultats. Elle peut être visualisée avec l'autocorrélogramme (ACF) qui montre la corrélation pour chaque décalage. Les barres qui dépassent la zone d'intervalle de confiance sont significativement corrélées avec la donnée au lag = 0.
### Mann-Kendall
Le test de Mann-Kendall est un test non paramétrique de tendance monotone. Il détecte s'il y a une tendance dans une seule direction en comparant chaque valeur à toutes les valeurs suivantes.
- **Hypothèses:** H0 = pas de tendance | H1 = tendance croissante ou décroissante.
- **Prémisses:** observations indépendantes (sans autocorrélation) et sans saisonnalité.
- **Variantes:**
    - *original*: la version de base
    - *Hamed-Rao*: corrige l'effet de l'autocorrélation
    - *saisonnier* (Hirsch): corrige l'effet de la saisonnalité en comparant par exemple chaque mois aux mêmes mois des autres années
    - *saisonnier corrélé* (Hirsch-Slack): comme le saisonnier, en tenant compte de la dépendance entre les mois.
- **Pente de Sen:** médiane des pentes entre toutes les paires de points. Elle quantifie la tendance.
- **Attention:** une p-value > 0,05 ne prouve pas nécessairement l'absence de tendance.
### Corrélation croisée
Comme avec l'autocorrélation, la corrélation croisée est la corrélation entre deux séries distinctes décalées (lag) dans le temps. Le décalage où la corrélation est maximale permet de connaitre quelle série est en avance sur l'autre et de quantifier cette avance.
- **Prémisses:** séries stationnaires (pas de tendance et de saisonnalité, variance constante)
- **Préblanchiment:** si les séries sont autocorrélées, la corrélation s'étale sur plusieurs lags. Pour corriger l'autocorrélation, on ajuste un modèle autorégressif (AR) sur une des séries pour ensuite l'appliquer sur les deux avant de faire la corrélation croisée.
- **Attention:** le pas de temps des données a un impact sur les décalages observés avec la corrélation croisée.
### Pettitt
Le test de Pettitt est un test non paramétrique qui détecte une seule rupture dans une série en identifiant un changement brusque de la médiane. Le test indique à quel moment la rupture survient.
- **Hypothèses:** H0 = pas de rupture | H1 = présence d'une rupture
- **Prémisses:** observations indépendantes (pas d'autocorrélation)
- **Attention:** quand les données sont autocorrélées, on doit faire attention à l'interprétation de la p-value, mais la position de la rupture peut être une information utile.
### Poisson
Le test de Poisson à deux échantillons est un test paramétrique qui compare le taux d'occurrence de deux populations entre eux pour déterminer s'ils sont significativement différents.
- **Hypothèses:** H0 = les deux taux sont égaux | H1 = les deux taux sont différents
- **Prémisses:** absence d'autocorrélation, rapport variance/moyenne proche de 1, taux constant à l'intérieur de chaque période.
- **Attention:** Le nombre d'observations influence la puissance du test. Plus le nombre d'événements est élevé (taux élevé ou longue période), plus le test peut détecter une différence.
### Mann-Whitney
Le test de Mann-Whitney est un test non paramétrique qui compare deux groupes indépendants à partir du rang des valeurs.
- **Hypothèses:** H0 = les deux groupes proviennent de la même distribution | H1 = les valeurs d'un des groupes tendent à être plus grandes que celles de l'autre
- **Prémisses:** absence de corrélation entre les groupes et absence d'autocorrélation.
- **Attention:** Le test de Mann-Whitney est robuste même en présence de valeurs extrêmes. Il est toutefois moins puissant quand les groupes sont petits.

## Contexte
Le laboratoire se fera en deux parties. La première servira surtout à explorer des données de séries temporelles alors que la deuxième pourra vous aider dans votre travail pour la présentation finale. J'essaie un format d'évaluation différent cette fois-ci. Je vais vous fournir une liste de questions pour vous aider à vous préparer. La dernière heure du cours est réservée pour l'évaluation qui se fera sous la forme de discussions individuelles.

## Pour démarrer l'interface MyBinder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/matrixGIS/GEO71021/main?urlpath=lab/tree/TP3/notebooks)
1. Cliquez sur le bouton **launch binder** ci-dessus (ça peut prendre quelques minutes la première fois).
2. Ouvrez la partie 1 dans le dossier `notebooks` pour débuter la première partie. Faites la même chose avec la 2e partie une fois que vous avez terminé avec la première.
3. Référez-vous au document fourni pour vous préparer à l'évaluation.

## Sauvegardez votre travail régulièrement
Une session MyBinder est **temporaire** : elle s'efface après environ 10 minutes d'inactivité ou à la fermeture de l'onglet.
Téléchargez votre notebook : **File > Download** (format `.ipynb`).
Pour reprendre, relancez MyBinder, puis glissez votre fichier dans le dossier `notebooks`.

## Données utilisées (`formatted_data/`)
| Fichier | Source | Pas de temps |
|---|---|---|
| `PaP_7056068_horaire.csv` | Environnement et Changement climatique Canada (Pointe-au-Père) | horaire, UTC |
| `MontJoli_7055122_horaire.csv` | Environnement et Changement climatique Canada (Mont-Joli) | horaire, UTC |
| `Neigette_021916_quotidien.csv` | CEHQ, Petite rivière Neigette (021916) | quotidien |
| `MontComi_15min.csv` | Station météorologique du Mont-Comi (UQAR) | 15 minutes, UTC |
