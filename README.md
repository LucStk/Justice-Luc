# Justice-Luc

Les fonctions python sont dans le fichier utile.py
Pour les faire fonctionner, il faut installer les librairies présentes dans le fichier requirements.txt ou exécuter la commande pip -r requirements.txt dans un terminal.


utiles.py comporte
- La fonction GenericClean qui les colonnes correspondant aux id des stations de départ et d'arrivé, rajoute la colonne 'durationmin', la durée de transport en minute. Ne prend que la première sortie d'une requête et supprime les deux autres instances.
- La fonction filtreTime qui prend le chemin du fichier csv et produit le fichier GenericStrasbourgFiltred.csv. Avec les lignes où la durée de temps est non indiqué (NaN) ou supérieur à 2 heures.
- La fonction filtreCondition. Détruit les lignes où l'ensemble des conditions ne sont pas à "Oui".

Le dossier test comporte un fichier py pour chaque fonction à tester. (ATTENTION, il faut cependant modifier la ligne path pour l'adapter à votre environnement)
