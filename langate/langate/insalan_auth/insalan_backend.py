# coding=utf-8
""" Insalan website authentication backend """
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpRequest

UserModel = get_user_model()


class InsalanBackend(ModelBackend):
    """
    A class extending ModelBackend to authenticate remote users from insalan.fr if they
    are not locals users.
    """

    # README : related documentation :
    # https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#available-authentication-backends

    def authenticate(self, request: HttpRequest, username: str = None, password: str = None, **kwargs):
        """
        authenticate() should check the credentials it gets and return a user object that matches those credentials
        if the credentials are valid. If they’re not valid, it should return None
        :param request: an HttpRequest and may be None if it was not provided
        :param username: a string, which is the username of the user
        :param password: a string, which is the password of the user
        :param kwargs: could contain the username at the key 'username'
        :return user : the user found if username and password are corrects and if he has the right to connect
        """
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            # Try to find user in local database
            # TODO : to simplify, by using two backend (the default one of django, as well as this one in fallback)
            user = UserModel._default_manager.get_by_natural_key(username)

            # User exists in local database
            if not (user.check_password(password) and self.user_can_authenticate(user)):
                # Wrong password
                raise ValidationError("Wrong username or password.")
            else:
                # Credentials are ok
                return user

        except UserModel.DoesNotExist:
            # User is missing from local database, we need to check insalan.fr
            """
            API optional request data
            { "tournaments": "t1,t2,..." }

            API response
            {
                "user": { "username": username },
                "err":  "registration_not_found",   (player not found)
                        "no_paid_place",            (player found but he has not paid)
                        None,                       (player found and he has paid)
                "tournament":   "manager"   (the person is a manager of one of the tournaments t1, t2, ...)
                                "t1"        (he is a player and registered in tournament t1)
                                None
            }
            For now we are not using tournament data, but we might use it in the future.            
            """

            # Request with authentication
            try:
                request_result = requests.get("https://www.insalan.fr/api/user/me", auth=(username, password), timeout=1)
            except requests.exceptions.Timeout:
                raise ValidationError("User not registered locally and remote API unreachable.")

            if request_result.status_code == 401:  # 401 = Unauthorized
                # Bad credentials
                raise ValidationError("Wrong username or password.")

            if request_result.status_code != 200:  # 200 = OK
                # The request failed because of something else
                raise LoginException

            # Credentials are ok in remote database
            try:
                json_result = request_result.json()
                paid_status = json_result["err"]
                if paid_status == "registration_not_found":
                    # The player is not registered in a tournament
                    # TODO : what to return ? failure ?
                    raise ValidationError("This player is not registered in any tournament.")
                elif paid_status == "no_paid_place":
                    # The player is registered but has not paid
                    raise ValidationError("This player is registered but has not paid.")
                else:
                    # The player has paid, we can return the object
                    user = User.objects.create_user(username=username,
                                                    email=None,
                                                    password=password)
                    return user
            except ValidationError:
		# FIXME
                raise ValidationError
            except:
                # TODO : should be more precise (PEP 8 : do not use bare except)
                # Wrong JSON object
                raise LoginException

    def get_user_id(self, attributes):
        # TODO : why is this function not implemented ? It is really useful ?
        """
        (Docstring to do)
        :param attributes:
        """
        NotImplemented


class LoginException(Exception):
    """
    Base class for exceptions in this module.
    """
    pass


class BadCredentialsException(LoginException):
    """
    Exception raised when the login or password doesn't match.
    """

    def __init__(self):
        pass


class NotAllowedException(LoginException, PermissionDenied):
    """
    Exception raised when the user entered good credentials but
        - was a player and didn't pay
        - was banned
    Attributes:
        username -- username related to the unsuccessful transaction
        message -- message related to the error
    """

    def __init__(self, username: str, message: str):
        self.username = username
        self.message = message

