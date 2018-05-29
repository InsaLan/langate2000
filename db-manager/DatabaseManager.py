import sqlite3
import requests

def hashFunction(s):

class DatabaseManager:
    # localDatabase
    # remoteDatabase
    DEFAULT_FILENAME = "local.db"

    def __init__(self):
        open(DEFAULT_FILENAME, 'x').close()
        self.localDatabase = sqlite3.connect(DEFAULT_FILENAME).cursor()
        self.localDatabase.execute("create table userPass (username text, password text)")
        self.localDatabase.execute("create table userObj (username text, object text)")

    def __init__(self, filename):
        self.localDatabase = sqlite3.connect(filename).cursor()
    
    def getUser(self, username, password):
        # Check local database
        self.localDatabase.execute("select password from userPass where username=?", (username,))
        result = self.localDatabase.fetchone()
        if result != None:
            # User is present in local database
            if password == result[0]:
                return User() # TODO
            else:
                raise WrongPasswordError
        else:
            # User is missing from local database
            result = requests.post("https://www.insalan.fr/api/user/me", data = {"username" : "", "password" : ""})
            resultJson = result.json()

    
    def addUser(self, user):
        self.localDatabase.execute("insert into userPass values (?, ?)", )
    
    def isLocal(self, user):
        return 
    
    def delUser(self, username): #id ?

    def getUserPassword(self, user):
    
    def getUsers(self):
    
    def getMachines(self, user):