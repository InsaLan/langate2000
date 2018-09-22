""" Insalan website authentication backend """
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import UserManager, User

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
        :param request: an HttpRequest and may be None if it wasn’t provided
        :param username: a string, which is the username of the user
        :param password: a string, which is the password of the user
        :param kwargs: could contain the username at the key 'username'
        :return user : the user found if username and password are corrects and if he has the right to connect
        """
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        # Example : django "official" version
        '''
        def authenticate(self, request , username = None, password = None, **kwargs):
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                UserModel().set_password(password)
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
        '''

        # TODO :
        # Get the json from web
        # If the credentials are correct and the player has payed
        if NotImplemented:
            user = User.objects.create_user(username=username,
                                            email=None,
                                            password=password)
        # If the credentials are correct and the player HASN'T payed
        elif NotImplemented:
            raise NotAllowedException(username, "This player is correctly registered but hasn't paid.")

        # Else
        else:
            raise BadCredentialsException()

        # TODO later :
        # Fill the profil automatically linked to the account with data (tournament, role)

        # Then return the user newly created
        return user

    def get_user_id(self, attributes):
        NotImplemented


class LoginException(Exception):
    """Base class for exceptions in this module."""
    pass


class BadCredentialsException(LoginException):
    """Exception raised when the login or password doesn't match.
    Attributes:
        None
    """

    def __init__(self):
        pass


class NotAllowedException(LoginException, PermissionDenied):
    """Exception raised when the user entered good credentials but
        - was a player and didn't pay
        - was banned
    Attributes:
        username -- username related to the unsuccessful transaction
        message -- message related to the error
    """

    def __init__(self, username: str, message: str):
        self.username = username
        self.message = message
