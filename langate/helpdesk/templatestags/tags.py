from django import template
from helpdesk.models import Ticket, Message


register = template.Library()


@register.simple_tag
def unread_notifications(requestUser):
    return Ticket.objects.filter(is_read=False, owner=requestUser).count()

    