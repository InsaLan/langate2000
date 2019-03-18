# Langate2000
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FInsalan-EquipeTechnique%2Finsalan-langate2000.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FInsalan-EquipeTechnique%2Finsalan-langate2000?ref=badge_shield)


Le langate, ou langate2000 pour les intimes sera le futur portail captif de l'insalan. L'interet de ce projet est de passer sur une technologie plus facilement maintenable, souple, d'ajouter des fonctionnalités à l'ancien portail (tel qu'un futur helpdesk, un dashboard plus utile pour les joueurs) ainsi que le rendre plus rapide grâce à l'usage d'IP sets.

## Règles de participation :
Les commits doivent avoir un titre en anglais, résumant en moins de 5 mots la mise à jour, ainsi qu'un corps (également en anglais) si necessaire : ```git commit -m "Title" -m "Additionnal text to provide precisions"```. Les titres doivent commencer par une majuscule, sans points, et les corps doivent commencer par une majuscule et se terminer par un point. 
Le code (variables ainsi que commentaires de documentation) doit être en anglais. 

## Déploiement
Pour déployer ce projet, il faut :
- Déplacez vous dans le dossier de django ```cd langate```
- Installer python 3 ainsi que pip et virtualenv
  - Sur debian  ```sudo apt install python3 python3-pip python3-virtualenv```
  - Sur archlinux ```sudo pacman -S python python-pip python-virtualenv```
- Vous pouvez optionnellement créer un virtualenv afin d'isoler les paquets python du système ```python3 -m venv venv``` et le sourcer ```source ./venv/bin/activate```
- Enfin, installez les dépendances python ```pip3 install -U -r ./requirements.txt```

Vous pouvez alors lancer le serveur de développement ```python3 manage.py runserver```


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FInsalan-EquipeTechnique%2Finsalan-langate2000.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FInsalan-EquipeTechnique%2Finsalan-langate2000?ref=badge_large)