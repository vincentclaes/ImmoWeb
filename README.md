# ImmoWeb

## But
Le script a pour but d'enregistrer les annonces en Belgique du site ImmoWeb selon des critères de recherches prédéfinis.
Ces données sont enregistrés sous format JSON. 

Sous condition de lancer régulièrement le script, cela permet, par après, d'avoir une meilleure vue sur les biens (évolution des prix, prix moyen, géolocalisation, nombre d'annonces par commune, par type de biens, ...). **Cette partie n'est pas développée actuellement.**

## Fonctionnement
1. Modifier les critères de recherche dans config/config.json (à faire une seule fois, sauf si vos critères changent)
2. Lancer le script. Il recupère pour chaque annonce de la recherche, les données suivantes : _loyer, charge, étage, nombre de chambres, nombres de salles d'eau, surface habitable, surface de la terrasse, état, adresse, classe PEB_
3. Analyser les données qui se trouve dans saved_classified.json et/ou les photos dans classifieds/_id Immoweb_


## Critères de recherche
Les critères de recherche doivent être indiqués dans config/config.json au format JSON.

**rent** est un boolean définissant le type de recherche (location = true, vente = false).

**apartement** est boolean définissant le type de bien (appartement = true, maison = false).

**postal_code** est une liste reprenant les codes postaux des communes sur lesquelles on souhaite faire notre recherche.

**photos** est un boolean permettant la sauvegarde des photos des annonces.

__min_*__ et __max_*__ sont des valeurs de recherche pour la surface, le prix et le nombre de chambre. Une valeur à 0 définit une absence de recherche sur ce critère.

**stop-time** est le nombre de secondes qui s'écoulent entre chaque requête pour une nouvelle annonce.


## Futur (_ou rêves_)
- [x] BUG : Récupération de l'adresse du bien seul (pas celle de l'agence immobilière)
- [x] Lancement quotidien sur Heroku (sans photo ou avec photo avec Amazon S3)
- [ ] Affichage sur une carte type Google Maps des annonces
- [ ] Calcul de prix moyens selon type de biens (# chambres, commune, ...)
- [ ] Identification de la localisation sur base de la description (nom de rue ou quartier)
- [ ] Identification des charges comprises


## Modules utilisés
Ce script utilise BeautifulSoup4 et requests.
