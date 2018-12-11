from enum import Enum

from django.db import models
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class State(Enum):
    """
    This enum represents the possible state of a ticket
    """
    O = "OPEN"
    U = "UPDATE"
    C = "CLOSE"
    W = "WAITING"


class Message(models.Model):
    pass


class OpeningMessage(Message):
    pass


class CommentMessage(Message):
    pass


class ClosingMessage(Message):
    pass



class Ticket(models.Model):
    """
    A ticket is a set of messages
    """
    message = models.TextField()
    date = models.DateField(
        auto_now=True
    )



"""
class Ticket(models.Model):
    
    the ticket model
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    state = models.CharField(
        max_lenght=1,
        default=State.O.value,
        choice=[(status, status.value) for status in State]
    )
    content = models.TextField()
    creation_date = models.DateField(
        auto_now=True)  # useful to track the ticket

    def close_ticket(self):
        self.state = State.C.value
"""