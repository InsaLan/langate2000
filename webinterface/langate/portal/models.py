from django.db import models

# Create your models here.

#Custom usermodel
from django.contrib.auth.models import User

class LanUser(models.Model):
    #README : content of base user model :
    #https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#django.contrib.auth.models.User
    #DOCU related : https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#extending-user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #Additionnal attributes
    hasPayed = models.BooleanField
    tournament = models.CharField(max_length=100)
    #Normalement il existe un moyen de gérer les groupes dans django, à voir...
    