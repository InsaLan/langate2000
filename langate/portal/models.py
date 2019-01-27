from enum import Enum

import logging
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from modules import network

# Create your models here.

event_logger = logging.getLogger('langate.events')


class Role(Enum):
    P = "Player"
    M = "Manager"
    G = "Guest"
    S = "Staff Member"
    A = "Administrator"


class Status(Enum):
    O = "ok"
    U = "unstable"
    F = "fail"


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


class RealtimeStatusWidget(models.Model):
    visible = models.BooleanField(default=False)
    lan = models.CharField(max_length=1, default=Status.O.value, choices=[(tag, tag.value) for tag in Status])
    wan = models.CharField(max_length=1, default=Status.O.value, choices=[(tag, tag.value) for tag in Status])
    csgo = models.CharField(max_length=1, default=Status.O.value, choices=[(tag, tag.value) for tag in Status])


class AnnounceWidget(models.Model):
    title = models.CharField(max_length=50, blank=False)
    content = models.TextField(blank=False)


class PizzaSlot(models.Model):
    orders_begin = models.TimeField()
    orders_end = models.TimeField()
    delivery = models.TimeField()


class PizzaWidget(models.Model):
    visible = models.BooleanField(default=False)
    online_order_url = models.URLField()


# Functions listening modifications of user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:

        if instance.is_staff:
            Profile.objects.create(user=instance, role=Role.A.value)
        else:
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

        instance.mac = network.get_mac(ip)
                
        instance.area = "LAN"  # FIXME: replace with a call to the networking module

        settings.NETWORK.connect_user(instance.mac)

        event_logger.info("Connected device {} (owned by {}) at {} to the internet.".format(instance.mac, instance.user.username, instance.ip))

        instance.save()


@receiver(post_delete, sender=Device)
def delete_device(sender, instance, **kwargs):
    # When deleting a device, we need to unregister it from the network.

    event_logger.info("Disconnected device {} (owned by {}) at {} of the internet.".format(instance.mac, instance.user.username, instance.ip))

    settings.NETWORK.disconnect_user(instance.mac)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

    event_logger.info("User {} logged in from device at {}.".format(user.username, client_ip))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

    event_logger.info("User {} logged out from device at {}.".format(user.username, client_ip))

