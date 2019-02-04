import logging

from django.contrib.auth.models import User

from rest_framework import serializers
from portal.models import *
from langate.settings import Tournament

event_logger = logging.getLogger("langate.events")


class DeviceSerializer(serializers.ModelSerializer):
    name = serializers.RegexField("^[^\\<\\>]+$", max_length=100)

    class Meta:
        model = Device
        fields = ["id", "ip", "mac", "area", "name"]
        read_only_fields = ["id", "ip", "mac", "area"]


class ProfileSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Role])
    tournament = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Tournament], allow_null=True)

    def validate_role(self, value):
        # By default, DRF does not handle natively Enums in Choice Fields,
        # getting round this by passing the value of the Enum when validating the field
        return value.value

    def validate_tournament(self, value):
        # By default, DRF does not handle natively Enums in Choice Fields,
        # getting round this by passing the value of the Enum when validating the field

        if value is None:  # Value can be none because an user can have no tournament if he's admin or staff member
            return None

        else:
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

        creator = self.context['request'].user  # https://stackoverflow.com/a/30203950
        event_logger.info("User {} ({}) was created by {}.".format(user.username, profile.role, creator.username))

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
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'is_staff', 'is_active', 'profile')


class AnnounceWidgetSerializer(serializers.ModelSerializer):
    title = serializers.RegexField("^[^\\<\\>]+$", max_length=50)
    content = serializers.RegexField("^[^\\<\\>]+$")

    class Meta:
        model = AnnounceWidget
        fields = ('id', 'visible', 'title', 'content')


class RealtimeStatusWidgetSerializer(serializers.ModelSerializer):
    visible = serializers.BooleanField(default=False)
    lan = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Status])
    wan = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Status])
    csgo = serializers.ChoiceField(choices=[(tag, tag.value) for tag in Status])

    def validate_lan(self, value):
        return value.name

    def validate_wan(self, value):
        return value.name

    def validate_csgo(self, value):
        return value.name

    def update(self, instance, validated_data):

        instance.visible = validated_data.get("visible", False)
        instance.lan = validated_data.get("lan", Status.O)
        instance.wan = validated_data.get("wan", Status.O)
        instance.csgo = validated_data.get("csgo", Status.O)

        instance.save()

        return instance

    class Meta:
        model = RealtimeStatusWidget
        fields = ('visible', 'lan', 'wan', 'csgo')


class PizzaSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PizzaSlot
        fields = ('id', 'orders_begin', 'orders_end', 'delivery')


class PizzaWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PizzaWidget
        fields = ["visible"]
