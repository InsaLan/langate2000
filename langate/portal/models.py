from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Role(Enum):
    P = "Player"
    M = "Manager"
    G = "Guest"
    S = "Staff Member"
    A = "Administrator"


class Profile(models.Model):
    # DOCU related : https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#extending-user
    # and https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Additionnal attributes
    role = models.CharField(
        max_length=1,
        default=Role.P,
        choices=[(tag, tag.value) for tag in Role]  # Choices is a list of Tuple
    )
    ## Relevant if player :
    has_paid = models.BooleanField(default=False)
    tournament = models.CharField(max_length=100)
    team = models.CharField(max_length=100)

    def remove_user(self):
        User.delete(self.user)
        self.delete()


# Functions listening modifications of user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
