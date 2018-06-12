#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Iterable, Dict, Set, List, Tuple
from datetime import datetime
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
class InvalidMacError(NetworkError):
    '''the mac address provided was invalid'''
class NotInSetError(NetworkError):
    '''can't query or delete this mac, not in set'''
class Network:
    name: str
    counter: bool
    skbinfo: bool
    markStart: int
    markMod: int
    nextAdd: int
    def __init__(self, name="langate", defaultTimeout=0, counter=True, marking=True, mark=(0,1)):
        self.name = name
        self.timeout = defaultTimeout
        self.counter = counter
        self.skbinfo = marking
        (self.markStart,self.markMod) = mark
        self.nextAdd = 0
        #CMD=sudo ipset create langate hash:mac -exist hashsize 4096 timeout 0 counters skbinfo
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

    def verifyMac(mac: str):
        return re.match(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', mac)

    def connectUser(self, mac: str, timeout=-1):
        #CMD=sudo ipset add langate 00:00:00:00:00:01 -exist timeout 0 skbmark 0
        if not Network.verifyMac(mac):
            raise InvalidMacError("'{}' is not a valid mac address".format(mac))

        connectArgs = ["sudo", "ipset", "add", self.name, mac, "-exist"]
        if timeout!=-1:
            connectArgs.append("timeout")
            connectArgs.append(str(timeout))
        if self.skbinfo:
            connectArgs.append("skbmark")
            connectArgs.append(str(hex(self.nextAdd+self.markStart)))
            self.nextAdd = (self.nextAdd+1) % self.markMod:

        result = run(connectArgs, stderr=PIPE, timeout=2)

        if result.returncode!=0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))



    def connectUsers(self, macs: Iterable[str]):
        for mac in macs:
            self.connectUser(mac)

    def disconnectUser(self, mac: str):
        #CMD=sudo ipset del langate 00:00:00:00:00:01
        if not Network.verifyMac(mac):
            raise InvalidMacError("'{}' is not a valid mac address".format(mac))
        disconnectArgs = ["sudo", "ipset", "del", self.name, mac, "-exist"]

        result = run(disconnectArgs, stderr=PIPE, timeout=2)

        if result.returncode!=0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

    def getUserStats(self, mac: str) -> (bool, int):
        if not Network.verifyMac(mac):
            raise InvalidMacError("'{}' is not a valid mac address".format(mac))

        testArgs = ["sudo", "ipset", "test", self.name, mac, "-q"]

        result = run(testArgs, timeout=2)

        if result.returncode!=0:
            return (False, 0)
        if not self.counter:
            return (True, 0)

        listArgs = ["sudo", "ipset", "list", self.name]
        result = run(listArgs, stdout=PIPE, timeout=2)
        out = result.stdout.decode("UTF-8")
        for line in out.splitlines():
            if re.match(mac.upper()+'.*', line):
                byte = re.search('bytes ([0-9]+)', line).group(1)
                return (True, int(byte))

    def clear(self):
        clearArgs = ["sudo", "ipset", "flush", self.name]
        result = run(clearArgs, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stde.decode("UTF-8"))

    def getAllConnected(self) -> Dict[str, int]:
        listArgs = ["sudo", "ipset", "list", self.name]
        result = run(listArgs, stdout=PIPE, timeout=2)
        out = result.stdout.decode("UTF-8")
        res = dict()
        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                if self.counter:
                    byte = re.search('bytes ([0-9]+)', line).group(1)
                else:
                    byte = 0
                res[mac] = byte
        return res

    def delete(self):
        clearArgs = ["sudo", "ipset", "destroy", self.name]
        result = run(clearArgs, stderr=PIPE, timeout=2)
        if result.returncode!=0:
            raise GenericNetwokError(result.stde.decode("UTF-8"))
        del self

    def logStatistics(self):
        NotImplemented

    def getUsersLogs(self) -> List[Tuple[datetime, Dict[str, int]]]:
        NotImplemented

    def getVpnLogs(self) -> List[Tuple[datetime, Dict[str, int]]]:
        NotImplemented

    def clearLogs(self, after=datetime.now()):
        NotImplemented

    def tryBalance(self) -> Dict[int, Set[str]]:
        NotImplemented

    def getBalance(self, vpnid = -1) -> Dict[int, Set[str]]:
        NotImplemented

    def getVpn(mac: str) -> int:
        NotImplemented

    def setVpn(mac: str, vpn: int):
        NotImplemented
