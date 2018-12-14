from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.conf import settings

from .serializers import DeviceSerializer, UserSerializer
from portal.models import Device

from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics

import random

# Create your views here.


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

        # Deleting the device you are currently on is not allowed via the API.
        # Instead the user can log out from the portal.

        client_ip = request.META.get('HTTP_X_FORWARDED_FOR')

        dev = self.get_device(ident, request.user)

        if dev.ip == client_ip:
            raise APIException("Deleting your current device is not allowed via the API.")

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
        info = settings.NETWORK.get_user_info(dev.mac)
        
        status = "up" if info[0] else "down"
        up = info[1][1]
        down = info[1][0]
        mark = info[2]

        return Response({"status": status, "upload": up, "download": down, "vpn": mark})


class UserList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


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

        return Response({"status": "ok"})
