""" Insalan website authentication backend """
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class InsalanBackend(ModelBackend):
    '''
    A class extending ModelBackend to authenticate remote users from insalan.fr if they
    are not locals users.
    '''

    #README : related documentation :
    #https://docs.djangoproject.com/en/2.0/ref/contrib/auth/#available-authentication-backends

    def authenticate(self, request : HttpRequest , username : str = None, password : str = None, **kwargs):
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

        #Example : django "official" version
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

        NotImplemented

    def get_user_id(self, attributes):
        NotImplemented