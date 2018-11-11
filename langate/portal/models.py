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

    # Additional attributes
    role = models.CharField(
        max_length=1,
        default=Role.P.value,
        choices=[(tag, tag.value) for tag in Role]  # Choices is a list of Tuple
    )

    # Relevant if player :
    tournament = models.CharField(max_length=100)
    team = models.CharField(max_length=100)

    def remove_user(self):
        User.delete(self.user)
        self.delete()


class Device(models.Model):
    # User of the device
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Name of the device
    name = models.CharField(max_length=100, default="Computer")

    # IP address of the device
    ip = models.CharField(max_length=15)

    # MAC address of the device
    mac = models.CharField(max_length=17)

    # Area of the device, i.e. LAN or WiFi
    area = models.CharField(max_length=4, default="LAN")

    def create(self, validated_data, **kwargs):
        # On creating a new device, we need to use the networking module to retrieve
        # some information : for example the MAC address or the area of the device based on the IP.

        mac = "ff:ff:ff:ff:ff:ff"  # FIXME: replace with a call to the networking module
        area = "LAN"  # FIXME: replace with a call to the networking module

        return Device(mac=mac, area=area, **validated_data)

    # FIXME : we should consider also the case when an user deletes its last device !

# Functions listening modifications of user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if(instance.is_staff):
            Profile.objects.create(user=instance, role=Role.A.value)
        else:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
