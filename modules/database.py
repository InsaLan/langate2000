from django.db import models
from re import fullmatch
import requests

"""
TODO :
hashing function
insalan.fr API
line 50 and 76 assumptions
new_database & export_database functions
"""

class UserDoesNotExistException(Exception):
    pass

class InvalidLoginException(Exception):
    pass

class UserNotInDatabaseException(Exception):
    pass

class UserAlreadyExistsException(Exception):
    pass

class UserIsDistantException(Exception):
    pass

class MachineAlreadyOnAccountException(Exception):
    pass

class MachineAlreadyExistsException(Exception):
    pass

class MachineNotRegisteredException(Exception):
    pass

def h(s):
    return ... # hashing function

def is_clear_pass(p):
    return (fullmatch(r"[0-9]{4}", p) != None)

class Role(Enum):
    PLAYER = 1
    MANAGER = 2
    STAFF = 3
    ADMIN = 4

class User(models.Model):
    user_id = models.AutoField(primary_key = True)
    is_local_user = models.BooleanField()
    role = models.IntegerField()
    tournament = models.CharField()
    has_paid = models.BooleanField()
    pseudonym = models.CharField()

    def __unicode__(self):
        return "{0} [{1};{2};{3};{4};{5}]".format(self.user_id, self.is_local_user,
            self.role, self.tournament, self.has_paid, self.pseudonym)

class UserPassword(models.Model):
    user = models.ForeignKey("User")
    password = models.CharField()

class UserMac(models.Model):
    user = models.ForeignKey("User")
    mac = models.CharField(max_length = 17)

class DatabaseManager:
    # Functions about users
    def login_user(pseudo, password):
        u = User.objects.get(pseudonym = pseudo)
        if u != None:
            # User exists in local database
            p = UserPassword.objects.get(user = u).password # no "== None" test, assumes every User has an entry in UserPassword

            # if the password is a PIN code it is registered without hashing
            if is_clear_pass(password):
                right_password = password == p
            else:
                right_password = h(password) == p
            
            if right_password:
                return u.user_id
            else:
                raise InvalidLoginException
        else:
            # We need to check the remote database
            result = requests.post("https://www.insalan.fr/api/user/me", data = {"username" : pseudo, "password" : password})
            resultJson = result.json()            
            # ...
            if ...:
                User.objects.create(...)
            elif ...: # Wrong password API answer
                raise InvalidLoginException
            else: # Missing user API answer
                raise UserDoesNotExistException

    def register_local_user(pseudo, password, role, tournament):
        u = User.objects.get(pseudonym = pseudo)
        if u != None:
            raise UserAlreadyExistsException
        u = User.objects.create(is_local_user = True, role = role,
            tournament = tournament, has_paid = True, pseudonym = pseudo) # assumes the new user has paid
        return u.user_id
    
    def set_user_role(user_id, role):
        u = User.objects.get(user_id = user_id)
        if u == None:
            raise UserNotInDatabaseException
        else:
            u.role = role
            u.save()
    
    # Functions about machines
    def register_machine_on_user(user_id, mac):
        u = User.objects.get(user_id = user_id)
        if u == None:
            raise UserNotInDatabaseException
        machine = UserMac.objects.get(mac = mac)
        if machine == None:
            # Unregistered machine
            UserMac.objects.create(user = u, mac = mac)
        else:
            if machine.user != u:
                # Machine already registered on another user
                raise MachineAlreadyExistsException
            else:
                # Machine already registered on this user
                raise MachineAlreadyOnAccountException
    
    def unregister_machine_on_user(mac):
        machine = UserMac.objects.get(mac = mac)
        if machine == None:
            # Unregistered machine
            raise MachineNotRegisteredException
        else:
            machine.delete()
    
    def get_machine_registration(mac):
        machine = UserMac.objects.get(mac = mac)
        if machine == None:
            # Unregistered machine
            raise MachineNotRegisteredException
        else:
            return machine.user.user_id
    
    def get_machines_by_user(user_id):
        u = User.objects.get(user_id = user_id)
        if u == None:
            raise UserNotInDatabaseException
        machines = UserMac.objects.filter(user = u)
        return [machine.mac for machine in machines]

    # Functions on local users
    def unregister_local_user(user_id):
        u = User.objects.get(user_id = user_id)
        if u == None:
            raise UserNotInDatabaseException
        elif not u.is_local_user:
            raise UserIsDistantException
        else:
            u.delete()
    
    def get_user_password(user_id):
        u = User.objects.get(user_id = user_id)
        if u == None:
            raise UserNotInDatabaseException
        elif not u.is_local_user:
            raise UserIsDistantException
        else:
            return u.password

    # Accessors on the whole database
    def get_list_users():
        return [user for user in User.objects.all()]

    def get_logged_machines():
        return [machine.mac for machine in UserMac.objects.all()]
    
    # Management
    def new_database():
        # TODO
    
    def export_database(dir):
        # TODO
