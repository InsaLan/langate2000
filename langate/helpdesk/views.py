from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required
from . import TicketForm
@login_required
def helpdesk(request):
    form = TicketForm.TicketForm()
    return render(request, 'helpdesk.html', {"form": form})

@staff_member_required
def admin(request): 
    return render(request, 'admin_front.html')
