import logging

from django.contrib.auth.models import User

from rest_framework import serializers
from portal.models import *

event_logger = logging.getLogger("langate.events")


class DeviceSerializer(serializers.ModelSerializer):
    name = serializers.RegexField("^[^\\<\\>]+$", max_length=100)

    class Meta:
        model = Device
        fields = ["id", "ip", "mac", "area", "name"]
        read_only_fields = ["id", "ip", "mac", "area"]

class WhiteListSerializer(serializers.ModelSerializer):
    name = serializers.RegexField("^[^\\<\\>]+$", max_length=100)

    class Meta:
        model = WhiteListDevice
        fields = ["id", "mac", "name"]
        read_only_fields = ["id","mac", "name"]


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
        fields = ('max_device_nb', 'role', 'tournament', 'team')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    # See Nested representations in DRF documentation
    # https://www.django-rest-framework.org/api-guide/serializers/#writable-nested-representations

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')

        is_staff = profile_data.get('role', Role.P.value) == Role.A.value

        user = User.objects.create(**validated_data, is_staff=is_staff)
        user.save()

        profile = Profile.objects.get(user=user)

        profile.role = profile_data.get('role', Role.P.value)
        profile.tournament = profile_data.get('tournament', None)
        profile.team = profile_data.get('team', None)
        profile.save()

        creator = self.context['request'].user  # https://stackoverflow.com/a/30203950
        event_logger.info("User {} ({}) was created by {}.".format(user.username, profile.role, creator.username))

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')  # the profile should always exist
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = profile_data.get('role', profile.role) == Role.A.value
        instance.save()

        profile.max_device_nb = profile_data.get('max_device_nb', 3)
        profile.role = profile_data.get('role', profile.role)
        profile.tournament = profile_data.get('tournament', profile.tournament)
        profile.team = profile_data.get('team', profile.team)

        profile.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email', 'is_active', 'profile')

class AnnounceSerializer(serializers.ModelSerializer):
    body = serializers.RegexField("^[^\\<\\>]+$")  # disallow < and > characters as they could be used for injections

    """
    def create(self, validated_data):
        markdown_body = validated_data.pop('body', "")
        html_body = Markdown().convert(markdown_body)

        blog = Blog.objects.create(**validated_data, body=html_body)
        blog.save()

        return blog

    def update(self, instance, validated_data):
        markdown_body = validated_data.get('body', "")

        instance.title = validated_data.get("title", None)
        instance.pub_date = validated_data.get("last_update_date", datetime.now())
        instance.pinned = validated_data.get("pinned", False)
        instance.visible = validated_data.get("visible", False)
        instance.body = Markdown().convert(markdown_body)

        instance.save()

        return instance
    """

    class Meta:
        model = Announces
        fields = ('id', 'title', 'last_update_date', 'pinned', 'visible', 'short' , 'body')
