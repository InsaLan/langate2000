from django.contrib.auth.models import User

from rest_framework import serializers
from portal.models import Device, Role, Profile


class DeviceSerializer(serializers.ModelSerializer):
    name = serializers.SlugField(max_length=100)

    class Meta:
        model = Device
        fields = ["id", "ip", "area", "name"]
        read_only_fields = ["id", "ip", "area"]


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Role])

    def validate_role(self, value):
        # By default, DRF does not handle natively Enums in Choice Fields,
        # getting round this by passing the value of the Enum when validating the field
        return value.value

    class Meta:
        model = Profile
        fields = ('role', 'tournament', 'team')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    # See Nested representations in DRF documentation
    # https://www.django-rest-framework.org/api-guide/serializers/#writable-nested-representations

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        user.save()

        profile = Profile.objects.get(user=user)
        profile.role = profile_data.get('role', profile.role)
        profile.tournament = profile_data.get('tournament', profile.tournament)
        profile.team = profile_data.get('team', profile.team)
        profile.save()

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile') # the profile should always exist
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()

        profile.role = profile_data.get('role', profile.role)
        profile.tournament = profile_data.get('tournament', profile.tournament)
        profile.team = profile_data.get('team', profile.team)

        profile.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_active', 'profile')
