# coding=utf-8
""" Insalan website authentication backend """
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.db import transaction

from portal.models import Role, Tournament

import traceback

UserModel = get_user_model()


class InsalanBackend(ModelBackend):
    """
    A class extending ModelBackend to authenticate remote users from insalan.fr if they are not local users (using the new API).
    """

    # README : related documentation :
    # https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#available-authentication-backends

    def short_name_to_tournament_enum(self, short_name):

        # Remember to check the keys (short codes) with the web !
        short_name_table = {
            "CSGO": Tournament.csgo,
            "TM": Tournament.tm,
            "lol": Tournament.lol
        }

        # remove year from short name
        # IMPORTANT: this assumes that the short name returned by the API is in format "shortYYYY"
        # where short is the short name and YYYY the year.
        # TODO remove this silly thing, it just makes things harder to debug
        name = short_name[:-4]

        if name in short_name_table:
            return short_name_table[name].value
        else:
            print(f"Tournament {short_name} not found")
            return None

    def authenticate(self, request: HttpRequest, username: str = None,
                     password: str = None, **kwargs):
        """
        authenticate() should check the credentials it gets and return a user object that matches those credentials
        if the credentials are valid. If they’re not valid, it should return None
        :param request: an HttpRequest and may be None if it was not provided
        :param username: a string, which is the username of the user
        :param password: a string, which is the password of the user
        :param kwargs: could contain the username at the key 'username'
        :return user : the user found if username and password are corrects and if he has the right to connect
        """

        """
        API optional request data
        { "tournaments": "t1,t2,..." }

        API response
        {
            "user": {
                "username": username,
                "name": name,
                "email": email
            },
            "err":  "registration_not_found", (player not found)
                    "no_paid_place", (player found but he has not paid)
                    null, (player found and he has paid)
            "tournament": [
                {
                    "shortname": (...),
                    "game_name": (...),
                    "team": (...),
                    "manager": true / false,
                    "has_paid": true / false
                }
            ]
        }
        """

        # Raising ValidationError exceptions

        # Request with authentication
        try:
            request_result = requests.get(
                "https://www.insalan.fr/api/user/2me",
                auth=(username.encode("utf-8"), password.encode("utf-8")),
                timeout=1)

        except requests.exceptions.Timeout:
            raise ValidationError(
                "User not registered locally and remote API unreachable.")

        if request_result.status_code == 401:  # 401 = Unauthorized
            # Bad credentials
            raise ValidationError("Wrong username or password.")

        if request_result.status_code != 200:  # 200 = OK
            # The request failed because of something else
            raise ValidationError("Request status code is not OK.")

        # Credentials are ok in remote database
        try:
            json_result = request_result.json()
            paid_status = json_result["err"]
            if paid_status == "registration_not_found":
                # The insalan.fr account exists, but the player
                # is not registered during the event
                raise ValidationError(
                    "The account exists, but this player is not registered.")
            elif paid_status == "no_paid_place":
                # The player is registered but has not paid
                raise ValidationError(
                    "This player is registered but has not paid.")
            else:
                # The player has paid, we can return the object
                email = json_result["user"]["email"]

                with transaction.atomic():
                    if User.objects.filter(username=username).exists():
                        return User.objects.get(username=username)

                    user = User.objects.create(
                        username=username,
                        email=email,
                        password=password)

                    for tournament in json_result["tournament"]:
                        if tournament["has_paid"]:
                            short_name = tournament["shortname"] if "shortname" in tournament else None
                            is_manager = tournament["manager"] if "manager" in tournament else False

                            user.profile.tournament = self.short_name_to_tournament_enum(short_name)
                            user.profile.team = tournament["team"] if "team" in tournament else None

                            if is_manager:
                                user.profile.role = Role.M.value

                            break
                    user.save()
                    return user

        except ValidationError as e:
            # Any validation error is rethrown
            raise ValidationError(e.message)

        except Exception:
            # Any other error must be converted to a ValidationError
            # so that the client does not crash.
            # Any other error is due to a wrong reading phase on the JSON object
            # i.e. a wrong format in this JSON object.
            traceback.print_exc()
            raise ValidationError("Unhandled error with remote API.")
