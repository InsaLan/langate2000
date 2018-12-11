from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from . import TicketForm
def helpdesk(request):
    if request.user.is_authenticated:
        form = TicketForm.TicketUserForm()
    else:
        form = TicketForm.TicketAnonymousForm()
    # check whether it's valid:
    if form.is_valid():
        print("ok!")
    return render(request, 'helpdesk.html', {"form": form})


@staff_member_required
def admin(request):
    return render(request, 'admin_front.html')