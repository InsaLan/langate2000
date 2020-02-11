# Langate2000

Le langate, ou langate2000 pour les intimes sera le futur portail captif de l'insalan. L'interet de ce projet est de passer sur une technologie plus facilement maintenable, souple, d'ajouter des fonctionnalités à l'ancien portail (tel qu'un futur helpdesk, un dashboard plus utile pour les joueurs) ainsi que le rendre plus rapide grâce à l'usage d'IP sets.

## Règles de participation :
Les commits doivent avoir un titre en anglais, résumant en moins de 5 mots la mise à jour, ainsi qu'un corps (également en anglais) si necessaire : ```git commit -m "Title" -m "Additionnal text to provide precisions"```. Les titres doivent commencer par une majuscule, sans points, et les corps doivent commencer par une majuscule et se terminer par un point. 
Le code (variables ainsi que commentaires de documentation) doit être en anglais. 

## Déploiement Production
- la commande ```make install``` permet de copier le service netcontrol dans le bon doosier, la commande doit être lançée lors du premier déploiement.
- la commande ```make build``` sert à build le docker de production avec pour nom "langate".
- la commande ```make run``` permet de démarrer un docker préalablement build, attention si un docker est déja en run il faut stop le docker avant de le run de nouveau.
- la commande ```make stop``` permet de stop un docker déja lancé.
- la commande ```make restart``` permet de relancer le docker en faisant un ```make stop``` puis un ```make run```.
## Déploiement Dévellopement
- la commande ```make install``` permet de copier le service netcontrol dans le bon doosier, la comm$
- la commande ```make builddev``` permet de build un docker de dévellopement sous le nom langate-dev avec Dockerfile.dev .
- la commande ```make rundev``` permet de lancer un docker de dévellopement, attention si un docker est déja lancé alros il faut stop le docker avant de run de nouveau.
- la commande ```make stopdev``` permet de stop un docker déja lancé.
