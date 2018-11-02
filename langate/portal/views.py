from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.


@staff_member_required
def management(request):
    users = User.objects.all()
    players_list = []
    for u in users:
        player = {
            "id": u.id,
            "name": u.username,
            "email": u.email,
            "role": u.profile.role,
            "tournament": u.profile.tournament,
            "team": u.profile.team
        }
        players_list.append(player)
    context = {"page_name": "management",
               "players_list": players_list}
    return render(request, 'portal/management.html', context)


@login_required
def connected(request):
    context = {"page_name": "connected"}
    return render(request, 'portal/connected.html', context)


def faq(request):
    context = {"page_name": "faq"}
    return render(request, 'portal/faq.html', context)
