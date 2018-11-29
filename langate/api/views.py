from django.core.exceptions import PermissionDenied

from .serializers import DeviceSerializer, UserSerializer
from portal.models import Device
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics

import random

# Create your views here.


class UserDeviceList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        qs = Device.objects.filter(user=request.user)
        serializer = DeviceSerializer(qs, many=True)
        return Response(serializer.data)


class UserDevice(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_device(self, ident, user):

        # FIXME: This can raise Device.DoesNotExist exception, not sure whether we should catch this...
        dev = Device.objects.get(id=ident)

        # If the API call is made by the device owner or an admin, we should proceed, otherwise we should abort
        if (dev.user == user) or user.is_staff():
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

        dev = self.get_device(ident, request.user)
        dev.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAdminUser,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserPasswordGenerator(APIView):
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, ident):

        # FIXME: This can raise User.DoesNotExist exception, not sure whether we should catch this...
        user = User.objects.get(id=ident)
        p = random.randint(1000, 9999)

        user.set_password(p)
        user.save()

        return Response({"password": p})
