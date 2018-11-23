
from rest_framework import serializers
from portal.models import Device
import re

class DeviceSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    def validate_name(self, value):
        """
        Check that the provided name is only composed of alphanumeric characters to prevent injections
        """
        if not re.match('^\w+$', value):
            raise serializers.ValidationError("Non-alphanumerical characters are not allowed.")
        return value

    class Meta:
        model = Device
        fields = ["id", "ip", "area", "name"]
        read_only_fields = ["id", "ip", "area"]
