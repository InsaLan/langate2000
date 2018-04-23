import os.path
import sqlite3
import http.client

def hashFunction(s):

class DatabaseManager:
    def __init__(self):
        # Open a connection to local database
        if not os.path.isfile("local.db"):
            open("local.db", 'x').close()
            localConnection = sqlite3.connect("local.db")
            self.localCursor = localConnection.cursor()
            self.localCursor.execute("create table users (user text, pass text)")
        else:
            localConnection = sqlite3.connect("local.db")
            self.localCursor = localConnection.cursor()
        self.remoteLogin = http.client.HTTPSConnection("www.insalan.fr/api")
        # Open a connection to remote database
    
    LOGIN_OK = 0
    USER_NOT_FOUND = 1
    WRONG_PASSWORD = 2

    def login(self, username, password):
        uh, ph = hashFunction(username), hashFunction(password)
        self.localCursor.execute("select pass from users where user=?", (uh,))
        result = localCursor.fetchone()
        if (result != None):
            # User is present in local database
            if (result[0] == ph):
                return LOGIN_OK
            else:
                return WRONG_PASSWORD
        else:
            # User is missing from local database
            remoteLogin.request("POST", "/api/user/me", ..., ...)
