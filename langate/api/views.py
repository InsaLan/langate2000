from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.conf import settings
import logging
from markdown import Markdown
import requests
from .serializers import *
from portal.models import *
from secret import admin_creds
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics

from modules import netcontrol

import random, json

# Create your views here.
event_logger = logging.getLogger("langate.events")

class DeviceListByName(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, name):
        u = User.objects.get(username=name)

        if u == request.user or request.user.is_staff:
            # A normal user should only have access to the list of its devices,
            # So, we check that the request user matches the ID passed in parameter.
            # Admin users have the right to consult anyone's list of devices.

            qs = Device.objects.filter(user=u)
            serializer = DeviceSerializer(qs, many=True)

            return Response(serializer.data)

        else:
            raise PermissionDenied


class DeviceList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, pk):
        u = User.objects.get(id=pk)

        if u == request.user or request.user.is_staff:
            # A normal user should only have access to the list of its devices,
            # So, we check that the request user matches the ID passed in parameter.
            # Admin users have the right to consult anyone's list of devices.

            qs = Device.objects.filter(user=u)
            serializer = DeviceSerializer(qs, many=True)

            return Response(serializer.data)

        else:
            raise PermissionDenied

class ChangeMark(APIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self,request,ident,mark):
        dev = Device.objects.get(id=ident)
        r = netcontrol.query("set_mark", { "mac": dev.mac, "mark": mark})
        if (r["success"]):
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeviceDetails(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_device(self, ident, user):

        # FIXME: This can raise Device.DoesNotExist exception, not sure whether we should catch this...
        dev = Device.objects.get(id=ident)

        # If the API call is made by the device owner or an admin, we should proceed, otherwise we should abort
        if (dev.user == user) or user.is_staff:
            return dev
        else:
            raise PermissionDenied

    def get(self, request, ident):
        dev = self.get_device(ident, request.user)
        serializer = DeviceSerializer(dev)
        return Response(serializer.data)

    def put(self, request, ident, format=None):
        dev = self.get_device(ident, request.user)

        serializer = DeviceSerializer(dev, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ident, format=None):

        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

        dev = self.get_device(ident, request.user)

        if dev.ip == client_ip:
            # If the user decides to remove the device he is currently on,
            # We remove the device and log him out.

            dev.delete()
            logout(request)

            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            dev.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceStatus(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get_device(self, ident, user):

        # FIXME: This can raise Device.DoesNotExist exception, not sure whether we should catch this...
        dev = Device.objects.get(id=ident)

        # If the API call is made by the device owner or an admin, we should proceed, otherwise we should abort
        if (dev.user == user) or user.is_staff:
            return dev
        else:
            raise PermissionDenied

    def get(self, request, ident):

        dev = self.get_device(ident, request.user)
        r = netcontrol.query("get_user_info", { "mac": dev.mac })
        info = r["info"]

        # FIXME: was removed from langate2000-netcontrol
        return Response({"mark": info["mark"]})

class UserList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, *args, **kwargs):
        u = self.get_object()
        event_logger.info("User {} ({}) was removed by {}.".format(u.username, u.profile.role, request.user.username))
        return super().delete(request, args, kwargs)


class UserPasswordManager(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, pk):

        # FIXME: This can raise User.DoesNotExist exception, not sure whether we should catch this...
        user = User.objects.get(id=pk)
        p = random.randint(1000, 9999)

        user.set_password(p)
        user.save()

        return Response({"password": p})

    def post(self, request, pk):

        # FIXME: This can raise User.DoesNotExist exception, not sure whether we should catch this...
        user = User.objects.get(id=pk)

        user.set_password(request.data["password"])
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AnnounceList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = Announces.objects.all()
    serializer_class = AnnounceSerializer


class AnnounceDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = Announces.objects.all()
    serializer_class = AnnounceSerializer


class MarkdownPreview(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request):
        return Response({"result": Markdown().convert(request.data["request"])})


class TeamPlayers(APIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self, request):
        teams = requests.get("https://www.insalan.fr/api/admin/placement", auth=(admin_creds[0], admin_creds[1]))
        return Response(teams.json()["participants"])


class Bandwidth(APIView):
    permission_classes = (permissions.IsAdminUser,)
    def get(self, request, ip):
        #TODO: load ip by config
        ip = requests.get("http://172.16.1.1:1312/?group-by=sip:1312")
        return Response(ip.json()[ip])