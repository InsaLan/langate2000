from django import template
from helpdesk.models import Ticket, Message


register = template.Library()


@register.simple_tag
def unread_notifications(requestUser):
    if requestUser.is_staff:
        return Ticket.objects.filter(state='OPEN').count() + Ticket.objects.filter(owner=requestUser, state='READ_BY_OWNER').count()
    else:
        return Ticket.objects.filter(owner=requestUser, state='READ_BY_ADMIN').count()
    

    