from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.db import models


# Create your models here
class Ticket(models.Model):
    """
    A ticket is a set of messages
    """
    is_read = models.BooleanField(default=True)
    last_read = models.DateField(null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    

class Message(models.Model):
    title   = models.CharField(max_length=50, null=True)
    content = models.TextField(blank=False, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date  = models.DateTimeField(auto_now=True)
