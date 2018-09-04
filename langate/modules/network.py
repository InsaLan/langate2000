#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Iterable, Dict, Set, List, Tuple
from time import time
from subprocess import run, PIPE, TimeoutExpired
import re

class NetworkError(RuntimeError):
    '''any error related to this module'''
class NetworkInitializationError(NetworkError):
    '''any error related to initialization'''
class SudoNotFoundError(NetworkInitializationError):
    '''sudo was not fount, is it installed?'''
class IpsetNotFoundError(NetworkInitializationError):
    '''ipset was not found, is it installed?'''
class PermissionDeniedError(NetworkInitializationError):
    '''permission request timedout or was denied, verify /etc/sudoers ?'''
class SetExistError(NetworkInitializationError):
    '''set with same name but different properties already exist'''
class UnknownInitializationError(NetworkInitializationError):
    '''something went wrong, IDK what'''
class GenericNetworkError(NetworkError):
    '''something went wrong, IDK what'''
class InvalidAddressError(NetworkError):
    '''the address provided was invalid'''
class UnknownAddress(NetworkError):
    '''no corresponding address was found'''
class NotInSetError(NetworkError):
    '''can't query or delete this mac, not in set'''
class FeatureDisabledError(NetworkError):
    '''a feature required for this method is disabled'''

class Ipset:
    name: str
    counter: bool
    skbinfo: bool
    markStart: int
    markMod: int
    nextAdd: int
    multiVpnMark: int
    userLogs: List[Tuple[time, Dict[str, int]]]
    vpnLogs: List[Tuple[time, Dict[int, int]]]
    lastUserMeasure: Dict[str, int]
    lastVpnMeasure: Dict[int, int]
    #create a new set
    def __init__(self, name="langate", defaultTimeout=0, counter=True, marking=True, mark=(0,1), multiVpnMark=4294967295):
        #CMD=sudo ipset create langate hash:mac -exist hashsize 4096 timeout 0 counters skbinfo
        self.name = name
        self.timeout = defaultTimeout
        self.counter = counter
        self.skbinfo = marking
        (self.markStart,self.markMod) = mark
        self.nextAdd = 0
        self.multiVpnMark = multiVpnMark
        if self.counter:
            self.userLogs = list()
            self.lastUserMeasure = dict()
            if self.skbinfo:
                self.vpnLogs = list()
                self.lastVpnMeasure = dict()
        creationArgs = ["sudo", "ipset", "create", self.name, "hash:mac", "-exist", "hashsize", "4096", "timeout", str(defaultTimeout)]
        if self.counter:
            creationArgs.append("counters")
        if self.skbinfo:
            creationArgs.append("skbinfo")

        try:
            result = run(creationArgs, stderr=PIPE, timeout=2)
        except FileNotFoundError:
            raise SudoNotFoundError("sudo was not found")
        except TimeoutExpired:
            raise PermissionDeniedError("permission request timed out")
        if result.returncode!=0:
            if re.match(r'.*command not found.*', result.stderr.decode("UTF-8")):
                raise IpsetNotFoundError("ipset was not found")
            if re.match(r'.*set with the same name already exists.*', result.stderr.decode("UTF-8")):
                raise SetExistError("set with same name but different settings already exist")
            raise UnknownInitializationError(result.stderr.decode("UTF-8"))

    #add a user to the set
    def connectUser(self, mac: str, timeout=None, mark=None,counter=0, multiVpn=False):
        #CMD=sudo ipset add langate 00:00:00:00:00:01 -exist timeout 0 skbmark 0
        if not NetworkUtil.verifyMac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        connectArgs = ["sudo", "ipset", "add", self.name, mac, "-exist"]
        if timeout!=None:
            connectArgs.append("timeout")
            connectArgs.append(str(timeout))
        if self.counter:
            connectArgs.append("bytes")
            connectArgs.append(str(counter))
        elif counter!=0:
            raise FeatureDisabledError("Feature counter is disables for this set")
        if self.skbinfo:
            connectArgs.append("skbmark")
            if multiVpn:
                connectArgs.append(hex(self.statelessMark))
            elif mark==None:
                connectArgs.append(hex(self.nextAdd+self.markStart))
                self.nextAdd = (self.nextAdd+1) % self.markMod
            else:
                connectArgs.append(hex(mark))
        elif mark!=None:
            raise FeatureDisabledError("Feature skbinfo is disables for this set")

        result = run(connectArgs, stderr=PIPE, timeout=2)

        if result.returncode!=0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))


    #add multiple mac to the set
    def connectUsers(self, macs: Iterable[str]):
        for mac in macs:
            self.connectUser(mac)

    #remove mac from the set
    def disconnectUser(self, mac: str):
        #CMD=sudo ipset del langate 00:00:00:00:00:01
        if not NetworkUtil.verifyMac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        disconnectArgs = ["sudo", "ipset", "del", self.name, mac, "-exist"]

        result = run(disconnectArgs, stderr=PIPE, timeout=2)

        if result.returncode!=0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

    #from mac, get if connected, how much bytes where transfered since connected and what mark is used by the entry
    def getUserInfo(self, mac: str) -> (bool, int, int):
        #CMD=sudo ipset test langate 00:00:00:00:00:01 -q
        #CMD=sudo ipset list langate | grep 00:00:00:00:00:01

        if not NetworkUtil.verifyMac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        testArgs = ["sudo", "ipset", "test", self.name, mac, "-q"]

        result = run(testArgs, timeout=2)

        if result.returncode!=0:
            return (False, 0, 0)
        if not self.counter and not self.skbmark:
            return (True, 0, 0)

        listArgs = ["sudo", "ipset", "list", self.name]
        result = run(listArgs, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        for line in out.splitlines():
            if re.match(mac.upper()+'.*', line):
                byte = re.search('bytes ([0-9]+)', line)
                if byte:
                    byte = int(byte.group(1))
                else:
                    byte=0
                skbmark = re.search('skbmark (0x[0-9]+)', line)
                if skbmark:
                    skbmark = int(skbmark.group(1),16)
                else:
                    skbmark = 0
                return (True, byte, skbmark)

    #remove all entry from the set
    def clear(self):
        #CMD=sudo ipset flush langate
        clearArgs = ["sudo", "ipset", "flush", self.name]
        result = run(clearArgs, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stderr.decode("UTF-8"))

    #get all entry from the set, with how much bytes thes transfered and what is their mark
    def getAllConnected(self) -> Dict[str, Tuple[int,int]]:
        #CMD=sudo ipset list langate
        listArgs = ["sudo", "ipset", "list", self.name]
        result = run(listArgs, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        res = dict()
        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = re.search('bytes ([0-9]+)', line)
                if byte:
                    byte = int(byte.group(1))
                else:
                    byte=0
                skbmark = re.search('skbmark (0x[0-9]+)', line)
                if skbmark:
                    skbmark = int(skbmark.group(1),16)
                else:
                    skbmark = 0
                res[mac] = (byte, skbmark)
        return res

    #delete the set (don't use is after or it will throws lots of exceptions
    def delete(self):
        #CMD=sudo ipset destroy langate
        clearArgs = ["sudo", "ipset", "destroy", self.name]
        result = run(clearArgs, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stde.decode("UTF-8"))
        del self

    #add an entry to internal log
    def logStatistics(self):
        #CMD=sudo ipset list langate

        if not self.counter:
            raise FeatureDisabledError("Feature counter is disables for this set")

        listArgs = ["sudo", "ipset", "list", self.name]
        result = run(listArgs, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")

        currentTime = time()
        userLog = dict()
        if self.skbinfo:
            vpnLog = dict()

        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = int(re.search('bytes ([0-9]+)', line).group(1))

                if mac in self.lastUserMeasure:
                    userLog[mac]=byte - self.lastUserMeasure[mac]
                else:
                    userLog[mac]=byte
                self.lastUserMeasure[mac]=byte
                if self.skbinfo:
                    vpn = re.search('skbmark (0x[0-9]+)', line)
                    if vpn:
                        vpn=int(vpn.group(1),16)
                    else:
                        continue
                    if vpn in vpnLog:
                        vpnLog[vpn]+=byte
                    else:
                        vpnLog[vpn]= byte

        self.userLogs.append((currentTime, userLog))

        if self.skbinfo:
            for vpn in vpnLog:
                if not vpn in self.lastVpnMeasure:
                    self.lastVpnMeasure[vpn] = 0
                vpnLog[vpn]-=self.lastVpnMeasure[vpn]
                self.lastVpnMeasure[vpn]+= vpnLog[vpn]
            self.vpnLogs.append((currentTime, vpnLog))


    #get logs, by user. Entries are sorted by date, tuple contain date and bytes transfered by mac since previous entry
    def getUsersLogs(self) -> List[Tuple[time, Dict[str, int]]]:
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disables for this set")
        return self.userLogs

    #get logs, by vpn. Entries are sorted by date, tuple contain date and bytes transfered by vpn since previous entry
    def getVpnLogs(self) -> List[Tuple[time, Dict[int, int]]]:
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disables for this set")
        if not self.skbinfo:
            raise FeatureDisabledError("Feature skbinfo is disables for this set")
        return self.vpnLogs

    #clear internal logs (logs are never cleared otherwise, taking memory indefinitely)
    def clearLogs(self, after=time()):
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disables for this set")
        self.userLogs = list()
        if self.skbinfo:
            self.vpnLogs = list()

    #try to auto-balance vpn usage by switching some user of vpn
    def tryBalance(self):
        NotImplemented

    #get current mapping of vpn and mac (each entry contain the vpn number, with who is connected to it)
    def getBalance(self) -> Dict[int, Set[str]]:
        res = dict()
        connected = self.getAllConnected()
        for mac in connected:
            if connected[mac][1] in res:
                res[connected[mac][1]].add(mac)
            else:
                res[connected[mac][1]] = set()
                res[connected[mac][1]].add(mac)
        return res

    #move someone to a new vpn
    def setVpn(self, mac: str, vpn: int):
        if not NetworkUtil.verifyMac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        if not self.skbinfo:
            raise FeatureDisabledError("Feature skbinfo is disables for this set")

        userInfo = self.getUserInfo(mac)
        if userInfo[0]:
            oldVpn = userInfo[2]
            byte = userInfo[1]
            self.connectUser(mac, mark=vpn, counter=byte)
            if self.counter:
                self.lastVpnMeasure[oldVpn] = self.lastVpnMeasure.get(oldVpn,0) - self.lastUserMeasure.get(mac,0)
                self.lastVpnMeasure[vpn] = self.lastVpnMeasure.get(vpn,0) + self.lastUserMeasure.get(mac,0)
        else:
            raise NotInSetError("'{}' is not in the set")


class NetworkUtil:

    #verify if mac is well formed
    def verifyMac(mac: str) -> bool:
        return bool(re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac))

    #verify is ip is well formed
    def verifyIp(ip: str) -> bool:
        return bool(re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', ip))

    #get ip from mac
    def getIp(mac: str) -> str:
        if not NetworkUtil.verifyMac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        f = open('/proc/net/arp', 'r')
        lines = f.readlines()[1:]
        for line in lines:
            if line.startswith(mac, 41):#41=offset in line
                return line.split(' ')[0]
        raise UnknownAddress("'{}' does not have a known ip".format(mac))

    #get mac from ip
    def getMac(ip: str) -> str:
        if not NetworkUtil.verifyIp(ip):
            raise InvalidAddressError("'{}' is not a valid ip address".format(ip))
        f = open('/proc/net/arp', 'r')
        lines = f.readlines()[1:]
        for line in lines:
            if line.startswith(ip, 0):#41=offset in line
                return line[41:].split(' ')[0]
        raise UnknownAddress("'{}' does not have a known mac".format(ip))
