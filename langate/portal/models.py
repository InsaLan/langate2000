from enum import Enum

import logging, random
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from rest_framework.compat import MinValueValidator

from modules import netcontrol

# Create your models here.

event_logger = logging.getLogger('langate.events')


def generate_dev_name():

    try:
        with open("misc/device_names.txt") as f:
            lines = f.read().splitlines()
            return random.choice(lines)

    except FileNotFoundError:
        return "Computer"


class Tournament(Enum):
    csgo = "Counter Strike Global Offensive"
    dota = "Dota 2"
    tft = "Team Fight Tactics"
    lol = "League Of Legends"


class Role(Enum):
    P = "Player"
    M = "Manager"
    G = "Guest"
    S = "Staff Member"
    A = "Administrator"


class Announces(models.Model):
    title = models.CharField(max_length=255)
    last_update_date = models.DateTimeField(auto_now=True, blank=True)

    pinned = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    short = models.BooleanField(default=True)

    summary = models.TextField()
    body = models.TextField()

class Profile(models.Model):
    # DOCU related : https://docs.djangoproject.com/en/2.0/topics/auth/customizing/#extending-user
    # and https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_device_nb = models.IntegerField(default=3, validators=[ MinValueValidator(limit_value=2) ])

    # Additional attributes
    role = models.CharField(
        max_length=1,
        default=Role.P.value,
        choices=[(tag, tag.value) for tag in Role]  # Choices is a list of Tuple
    )

    # Relevant if player :
    tournament = models.CharField(max_length=100, null=True)
    team = models.CharField(max_length=100, null=True)

    def remove_user(self):
        User.delete(self.user)
        self.delete()


class Device(models.Model):
    # User of the device
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Name of the device
    name = models.CharField(max_length=100, default="Computer")

    # IP address of the device
    ip = models.CharField(max_length=15, blank=False)  # One device should have an IP, the MAC is filled based on it.

    # MAC address of the device
    mac = models.CharField(max_length=17) # One device = 1 MAC = One User, two users cannot have the same device !

    # Area of the device, i.e. LAN or WiFi
    area = models.CharField(max_length=4, default="LAN")

class WhiteListDevice(models.Model):

    # Name of the device
    name = models.CharField(max_length=100, default="Server")

    # MAC address of the device
    mac = models.CharField(max_length=17) # One device = 1 MAC = One User, two users cannot have the same device !



# Functions listening modifications of user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Device)
def create_device(sender, instance, created, **kwargs):
    # On creating a new device, we need to use the networking module to retrieve
    # some information : for example the MAC address or the area of the device based on the IP.

    if created:
        ip = instance.ip  # IP should exist at this stage and it will fail really bad if it doesn't.

        instance.name = generate_dev_name()

        r = netcontrol.query("get_mac", { "ip": ip })

        instance.mac = r["mac"]
        instance.area = "LAN"  # FIXME: replace with a call to the networking module

        netcontrol.query("connect_user", { "mac": instance.mac, "name": instance.user.username })

        event_logger.info("Connected device {} (owned by {}) at {} to the internet.".format(instance.mac, instance.user.username, instance.ip))

        instance.save()


@receiver(post_delete, sender=Device)
def delete_device(sender, instance, **kwargs):
    # When deleting a device, we need to unregister it from the network.

    event_logger.info("Disconnected device {} (owned by {}) at {} of the internet.".format(instance.mac, instance.user.username, instance.ip))

    netcontrol.query("disconnect_user", { "mac": instance.mac })


@receiver(post_save, sender=WhiteListDevice)
def create_whitelist_device(sender, instance, created, **kwargs):
    # On creating a new device, we need to use the networking module to retrieve
    # some information : for example the MAC address or the area of the device based on the IP.

    if created:
        mac = instance.mac
        name = instance.name

        netcontrol.query("connect_user", { "mac": instance.mac, "name": instance.name })

        event_logger.info("Connected device {} (the mac {} has been connected)".format(instance.mac, instance.name))

        instance.save()


@receiver(post_delete, sender=WhiteListDevice)
def delete_whitelist_device(sender, instance, **kwargs):
    # When deleting a device, we need to unregister it from the network.

    event_logger.info("Disconnected device {} (the mac {} has been disconnected) ".format(instance.mac, instance.name))

    netcontrol.query("disconnect_user", { "mac": instance.mac })
