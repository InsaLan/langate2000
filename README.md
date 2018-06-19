# Langate2000

Le langate, ou langate2000 pour les intimes sera le futur portail captif de l'insalan. L'interet de ce projet est de passer sur une technologie plus facilement maintenable, souple, d'ajouter des fonctionnalités à l'ancien portail (tel qu'un futur helpdesk, un dashboard plus utile pour les joueurs) ainsi que le rendre plus rapide grâce à l'usage d'IP sets.

## Règles de participation :
Les commits doivent avoir un titre en anglais, résumant en moins de 5 mots la mise à jour, ainsi qu'un corps (également en anglais) si necessaire : ```git commit -m "Title" -m "Additionnal text to provide precisions"```. Les titres doivent commencer par une majuscule, sans points, et les corps doivent commencer par une majuscule et se terminer par un point. 
Le code (variables ainsi que commentaires de documentation) doit être en anglais. 

## Déploiement
Pour déployer ce projet, il faut :
- Installer python 3 ainsi que pip : ```sudo apt-get install -y python3 python3-pip```
- Installer django 2 : ```sudo pip3 install django```
Vous pouvez alors lancer le serveur de développement ```python3 webinterface/langate/manage.py runserver```
