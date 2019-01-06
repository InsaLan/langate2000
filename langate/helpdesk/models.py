from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.db import models
import datetime

# Create your models here
class Ticket(models.Model):
    """
    A ticket is a set of messages
    """
    title = models.CharField(max_length=50, null=True)
    is_read = models.BooleanField(default=True)
    last_read = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_closed = models.BooleanField(default=False)



    def __str__(self):
        return self.title


class Message(models.Model):
    content = models.TextField(blank=False, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date  = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.content
    def get_author(self):
        return self.sender