from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Device


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
    context = {"page_name": "connected", "too_many_devices": False, "devices_list": []}

    user_devices = Device.objects.filter(user=request.user)
    client_ip = request.META.get('REMOTE_ADDR')

    # Checking if the device accessing the gate is already in user devices

    if not user_devices.filter(ip=client_ip).exists():

        if len(user_devices) > 2:
            # If user has too much devices already registered, then we can't connect the device to the internet.
            # We will let him choose to remove one of them.

            context["too_many_devices"] = True

        else:
            # We can add the client device to the user devices.
            # FIXME: MAC address should be filled by a model receiver call to the networking module.

            dev = Device(user=request.user, ip=client_ip)
            dev.save()

    # Passing user devices to the template

    user_devices = Device.objects.filter(user=request.user)
    i = 1

    for d in user_devices:
        dev = {
            "count": i,
            "id": d.id,
            "area": d.area,
            "current_client": (d.ip == client_ip)
        }

        i += 1
        context["devices_list"].append(dev)

    return render(request, 'portal/connected.html', context)


def faq(request):
    context = {"page_name": "faq"}
    return render(request, 'portal/faq.html', context)


def test(request):
    user = {"name": "Imusho", "realname": "Trinity Pointard"}
    devices = [
            {"type": "Windows", "connexion": "Wired", "connected": True,
                "ip": "127.0.0.1", "mac": "FF:FF:FF:FF:FF:FF"},
            {"type": "Android", "connexion": "Wifi", "connected": False,
                "ip": "127.0.0.2", "mac": "FF:FF:FF:FF:FF:FE"},
        ]
    context = {"page_name": "User details", "user": user, "devices": devices}
    return render(request, 'portal/userDetails.html', context)
