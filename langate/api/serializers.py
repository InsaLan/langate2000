
from rest_framework import serializers
from portal.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        model = Device
        fields = ["id", "ip", "area", "name"]
        read_only_fields = ["id", "ip", "area"]
