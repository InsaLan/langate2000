from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth import logout , login
from django.conf import settings

import logging
from markdown import Markdown

from .serializers import *
from portal.models import *

from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from .serializers import UserSerializer, RegisterSerializer


from modules import netcontrol

import random, json

# Create your views here.
event_logger = logging.getLogger("langate.events")



# Register API
class RegisterAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": Token.objects.create(user=user)
        })

class LoginAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)#return une autre response quand le login fail
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceList(generics.ListAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer


class UserDeviceList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        u = User.objects.get(id=pk)

        if u == request.user or request.user.is_staff:
            # A normal user should only have access to the list of its devices,
            # So, we check that the request user matches the ID passed in parameter.
            # Admin users have the right to consult anyone's list of devices.

            qs = Device.objects.filter(user=u)
            serializer = UserDeviceSerializer(qs, many=True)

            return Response(serializer.data)

        else:
            raise PermissionDenied


class WhitelistList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    queryset = WhiteListDevice.objects.all()
    serializer_class = WhiteListSerializer


class WhitelistDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = WhiteListDevice.objects.all()
    serializer_class = WhiteListSerializer


class ChangeMark(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, ident, mark):

        if Device.objects.filter(id=ident).count() > 0:
            dev = Device.objects.get(id=ident)
            r = netcontrol.query("set_mark", {"mac": dev.mac, "mark": mark})

            if r["success"]:
                return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDeviceDetails(APIView):
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
        serializer = UserDeviceSerializer(dev)
        return Response(serializer.data)

    def put(self, request, ident, format=None):
        dev = self.get_device(ident, request.user)

        serializer = UserDeviceSerializer(dev, data=request.data)

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

class IsConnected(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request):
        user_devices = Device.objects.filter(user=request.user)
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

        context = {"page_name": "connected",
                "too_many_devices": False,
                "current_ip": client_ip,
                "is_announce_panel_visible": Announces.objects.filter(visible=True).count() > 0,
                "pinned_announces": Announces.objects.filter(pinned=True).order_by('-last_update_date'),
                "announces": Announces.objects.filter(pinned=False).order_by('-last_update_date'),
                "device_quota": request.user.profile.max_device_nb}

        # Checking if the device accessing the gate is already in user devices

        if not user_devices.filter(ip=client_ip).exists():

            #client_mac = network.get_mac(client_ip)

            r = netcontrol.query("get_mac", { "ip": client_ip })
            client_mac = r["mac"]

            if Device.objects.filter(mac=client_mac).count() > 0:

                # If the device MAC is already registered on the network but with a different IP,
                # * If the registered device is owned by the requesting user, we change the IP of the registered device.
                # * If the registered device is owned by another user, we delete the old device and we register the new one.
                # This could happen if the DHCP has changed the IP of the client.

                # The following should never raise a MultipleObjectsReturned exception
                # because it would mean that there are more than one devices
                # already registered with the same MAC.

                dev = Device.objects.get(mac=client_mac)

                if request.user != dev.user:
                    dev.delete()

                    new_dev = Device(user=request.user, ip=client_ip)
                    new_dev.save()

                else:
                    dev.ip = client_ip  # We edit the IP to reflect the change.
                    dev.save()

            elif len(user_devices) >= request.user.profile.max_device_nb:
                # If user has too much devices already registered, then we can't connect the device to the internet.
                # We will let him choose to remove one of them.

                context["too_many_devices"] = True

            else:
                # We can add the client device to the user devices.
                # See the networking functions in the receivers in portal/models.py

                dev = Device(user=request.user, ip=client_ip)
                dev.save()
        return Response(context)

class Disconnect(APIView):
    def get(self,request):
        user_devices = Device.objects.filter(user=request.user)
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

        if user_devices.filter(ip=client_ip).exists():
            # When the user decides to disconnect from the portal from a device,
            # we remove the Device from the array (if it still exists) and then we log the user out.

            user_devices.filter(ip=client_ip).delete()
            logout(request)
        return Response({"URL":"google.com"})#redirige vers notre page de login vue langate
        
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
