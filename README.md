# ImmoWeb

## Modules utilisés
Ce script utilise BeautifulSoup4 et requests.

## Critères de recherche
Les critères de recherche doivent être indiqués dans config/config.json au format JSON.
* *rent* * est un boolean définissant le type de recherche (location = true, vente = false)
* *apartement* * est boolean définissant le type de bien (appartement = true, maison = false)
* *postal_code* * est une liste reprenant les codes postaux des communes sur lesquelles on souhaite faire notre recherche
* *photos* * est un boolean permettant la sauvegarde des photos des annonces.
_ _min_*_ _ et _ _max_*_ _ sont des valeurs de recherche pour la surface, le prix et le nombre de chambre. Une valeur à 0 définit une absence de recherche sur ce critère.

## Fonctionnement
1. Modifier les critères de recherche dans config/config.json (à faire une seule fois, sauf si vos critères changent)
2. Lancer le script
3. Analyser les données qui se trouve dans saved_classified.json et/ou les photos dans classifieds/_ _*_ _



