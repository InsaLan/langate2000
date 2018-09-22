from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    # DOCU related : https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#extending-user
    # and https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additionnal attributes
    ##Relevant if player :
    tournament = models.CharField(max_length=100)
    team = models.CharField(max_length=100)


# Functions listening modifications of user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
