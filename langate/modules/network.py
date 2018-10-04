#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from typing import Iterable, Dict, Set, List, Tuple
from time import time
from subprocess import run, PIPE, TimeoutExpired
import re


class NetworkError(RuntimeError):
    """any error related to this module"""


class NetworkInitializationError(NetworkError):
    """any error related to initialization"""


class SudoNotFoundError(NetworkInitializationError):
    """sudo was not fount, is it installed?"""


class IpsetNotFoundError(NetworkInitializationError):
    """ipset was not found, is it installed?"""


class PermissionDeniedError(NetworkInitializationError):
    """permission request timedout or was denied, verify /etc/sudoers ?"""


class SetExistError(NetworkInitializationError):
    """set with same name but different properties already exist"""


class UnknownInitializationError(NetworkInitializationError):
    """something went wrong, IDK what"""


class GenericNetworkError(NetworkError):
    """something went wrong, IDK what"""


class InvalidAddressError(NetworkError):
    """the address provided was invalid"""


class UnknownAddress(NetworkError):
    """no corresponding address was found"""


class NotInSetError(NetworkError):
    """can't query or delete this mac, not in set"""


class FeatureDisabledError(NetworkError):
    """a feature required for this method is disabled"""


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

    # create a new set
    def __init__(self, name="langate", default_timeout=0, counter=True, marking=True, mark=(0, 1),
                 multi_vpn_mark=4294967295, fixed_vpn_timeout=30):
        # CMD=sudo ipset create langate hash:mac -exist hashsize 4096 timeout 0 counters skbinfo
        self.name = name
        self.timeout = default_timeout
        self.counter = counter
        self.skbinfo = marking
        (self.markStart, self.markMod) = mark
        self.nextAdd = 0
        self.multiVpnMark = multi_vpn_mark
        if self.counter:
            self.userLogs = list()
            self.lastUserMeasure = dict()
            if self.skbinfo:
                self.vpnLogs = list()
                self.lastVpnMeasure = dict()
        creation_args = ["sudo", "ipset", "create", self.name, "hash:mac", "-exist", "hashsize", "4096", "timeout",
                         str(default_timeout)]
        if self.counter:
            creation_args.append("counters")
        if self.skbinfo:
            creation_args.append("skbinfo")

        try:
            result = run(creation_args, stderr=PIPE, timeout=2)
        except FileNotFoundError:
            raise SudoNotFoundError("sudo was not found")
        except TimeoutExpired:
            raise PermissionDeniedError("permission request timed out")
        if result.returncode != 0:
            if re.match(r'.*command not found.*', result.stderr.decode("UTF-8")):
                raise IpsetNotFoundError("ipset was not found")
            if re.match(r'.*set with the same name already exists.*', result.stderr.decode("UTF-8")):
                raise SetExistError("set with same name but different settings already exist")
            raise UnknownInitializationError(result.stderr.decode("UTF-8"))
        if self.counter and self.skbinfo:
            # CMD=sudo ipset create langate-recent hash:mac -exist hashsize 4096 timeout 60
            creation_args = ["sudo", "ipset", "create", self.name + "-recent", "hash:mac", "-exist", "hashsize", "4096",
                             "timeout", str(fixed_vpn_timeout)]
            result = run(creation_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise UnknownInitializationError(result.stderr.decode("UTF-8"))

    # add a user to the set
    def connect_user(self, mac: str, timeout=None, mark=None, counter=0, multi_vpn=False):
        # CMD=sudo ipset add langate 00:00:00:00:00:01 -exist timeout 0 skbmark 0
        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        connect_args = ["sudo", "ipset", "add", self.name, mac, "-exist"]
        if timeout is not None:
            connect_args.append("timeout")
            connect_args.append(str(timeout))
        if self.counter:
            connect_args.append("bytes")
            connect_args.append(str(counter))
        elif counter != 0:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        if self.skbinfo:
            connect_args.append("skbmark")
            if multi_vpn:
                connect_args.append(hex(self.multiVpnMark))
            elif mark is None:
                connect_args.append(hex(self.nextAdd + self.markStart))
                self.nextAdd = (self.nextAdd + 1) % self.markMod
            else:
                connect_args.append(hex(mark))
        elif mark is not None:
            raise FeatureDisabledError("Feature skbinfo is disabled for this set")

        result = run(connect_args, stderr=PIPE, timeout=2)

        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

    # remove mac from the set
    def disconnect_user(self, mac: str):
        # CMD=sudo ipset del langate 00:00:00:00:00:01
        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        disconnect_args = ["sudo", "ipset", "del", self.name, mac, "-exist"]

        result = run(disconnect_args, stderr=PIPE, timeout=2)

        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

    # from mac, get if connected, how much bytes where transfered since connected and what mark is used by the entry
    def get_user_info(self, mac: str) -> (bool, int, int):
        # CMD=sudo ipset test langate 00:00:00:00:00:01 -q
        # CMD=sudo ipset list langate | grep 00:00:00:00:00:01

        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        test_args = ["sudo", "ipset", "test", self.name, mac, "-q"]

        result = run(test_args, timeout=2)

        if result.returncode != 0:
            return False, 0, 0
        if not self.counter and not self.skbinfo:
            return True, 0, 0

        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        for line in out.splitlines():
            if re.match(mac.upper() + '.*', line):
                byte = re.search('bytes ([0-9]+)', line)
                if byte:
                    byte = int(byte.group(1))
                else:
                    byte = 0
                skbmark = re.search('skbmark (0x[0-9]+)', line)
                if skbmark:
                    skbmark = int(skbmark.group(1), 16)
                else:
                    skbmark = 0
                return True, byte, skbmark

    # remove all entry from the set
    def clear(self):
        # CMD=sudo ipset flush langate
        clear_args = ["sudo", "ipset", "flush", self.name]
        result = run(clear_args, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

    # get all entry from the set, with how much bytes thes transfered and what is their mark
    def get_all_connected(self) -> Dict[str, Tuple[int, int]]:
        # CMD=sudo ipset list langate
        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        res = dict()
        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = re.search('bytes ([0-9]+)', line)
                if byte:
                    byte = int(byte.group(1))
                else:
                    byte = 0
                skbmark = re.search('skbmark (0x[0-9]+)', line)
                if skbmark:
                    skbmark = int(skbmark.group(1), 16)
                else:
                    skbmark = 0
                res[mac] = (byte, skbmark)
        return res

    # delete the set (don't use is after or it will throws lots of exceptions
    def delete(self):
        # CMD=sudo ipset destroy langate
        clear_args = ["sudo", "ipset", "destroy", self.name]
        result = run(clear_args, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        del self

    # add an entry to internal log
    def log_statistics(self):
        # CMD=sudo ipset list langate

        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")

        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")

        current_time = time()
        user_log = dict()
        if self.skbinfo:
            vpn_log = defaultdict(lambda: 0, {})

        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = int(re.search('bytes ([0-9]+)', line).group(1))

                if mac in self.lastUserMeasure:
                    user_log[mac] = byte - self.lastUserMeasure[mac]
                else:
                    user_log[mac] = byte
                self.lastUserMeasure[mac] = byte
                if self.skbinfo:
                    vpn = re.search('skbmark (0x[0-9]+)', line)
                    if vpn:
                        vpn = int(vpn.group(1), 16)
                    else:
                        continue
                    vpn_log[vpn] += byte

        self.userLogs.append((current_time, user_log))

        if self.skbinfo:
            for vpn in vpn_log:
                if vpn not in self.lastVpnMeasure:
                    self.lastVpnMeasure[vpn] = 0
                vpn_log[vpn] -= self.lastVpnMeasure[vpn]
                self.lastVpnMeasure[vpn] += vpn_log[vpn]
            self.vpnLogs.append((current_time, vpn_log))

    # get logs, by user. Entries are sorted by date, tuple contain date and bytes transfered by mac since previous entry
    def get_users_logs(self) -> List[Tuple[time, Dict[str, int]]]:
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        return self.userLogs

    # get logs, by vpn. Entries are sorted by date, tuple contain date and bytes transfered by vpn since previous entry
    def get_vpn_logs(self) -> List[Tuple[time, Dict[int, int]]]:
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        if not self.skbinfo:
            raise FeatureDisabledError("Feature skbinfo is disabled for this set")
        return self.vpnLogs

    # clear internal logs (logs are never cleared otherwise, taking memory indefinitely)
    def clear_logs(self, after=time()):
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        lo = 0
        hi = len(self.userLogs)
        while lo < hi:
            mid = (lo+hi)//2
            if self.userLogs[mid][0] < after: lo = mid+1
            else: hi = mid
        index = lo
        self.userLogs = self.userLogs[index:]
        if self.skbinfo:
            self.vpnLogs = self.vpnLogs[index:]

    # try to auto-balance vpn usage by switching some user of vpn
    def try_balance(self):
        # CMD=sudo ipset list langate
        if self.counter and self.skbinfo:
            # get users recent network usage
            logs = self.get_users_logs()
            if len(logs) > 0: log = logs[-1][1]
            else: return
            user_info = self.get_all_connected()
            all_connected = set(user_info)

            # get all fixed users
            list_args = ["sudo", "ipset", "list", self.name]
            result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))
            out = result.stdout.decode("UTF-8")
            fixed = set()
            for line in out.splitlines():
                if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                    mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                    fixed.add(mac)

            can_move = all_connected - fixed
            vpn_usage = defaultdict(lambda: 0, {})

            for player in fixed:
                vpn_usage[user_info[player][1]] += log[player]

            can_move = sorted(can_move, key=lambda p: log[p], reverse=True)

            vpn = sorted(vpn_usage, key=lambda v: vpn_usage[v])
            for player in can_move:
                vpn_usage[vpn[0]] += log[player]
                set_vpn(player, vpn[0])
                vpn = sorted(vpn, key=lambda v: vpn_usage[v])

        else:
            raise FeatureDisabledError("Feature counter or skbinfo is disabled for this set")

    # get current mapping of vpn and mac (each entry contain the vpn number, with who is connected to it)
    def get_balance(self) -> Dict[int, Set[str]]:
        res = dict()
        connected = self.get_all_connected()
        for mac in connected:
            if connected[mac][1] in res:
                res[connected[mac][1]].add(mac)
            else:
                res[connected[mac][1]] = set()
                res[connected[mac][1]].add(mac)
        return res

    # move someone to a new vpn
    def set_vpn(self, mac: str, vpn: int):
        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        if not self.skbinfo:
            raise FeatureDisabledError("Feature skbinfo is disabled for this set")

        user_info = self.get_user_info(mac)
        if user_info[0]:
            old_vpn = user_info[2]
            byte = user_info[1]
            self.connect_user(mac, mark=vpn, counter=byte)
            if self.counter:
                self.lastVpnMeasure[old_vpn] = self.lastVpnMeasure.get(old_vpn, 0) - self.lastUserMeasure.get(mac, 0)
                self.lastVpnMeasure[vpn] = self.lastVpnMeasure.get(vpn, 0) + self.lastUserMeasure.get(mac, 0)
        else:
            raise NotInSetError("'{}' is not in the set")


# verify if mac is well formed
def verify_mac(mac: str) -> bool:
    return bool(re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac))


# verify is ip is well formed
def verify_ip(ip: str) -> bool:
    return bool(re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', ip))


# get ip from mac
def get_ip(mac: str) -> str:
    if not verify_mac(mac):
        raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
    f = open('/proc/net/arp', 'r')
    lines = f.readlines()[1:]
    for line in lines:
        if line.startswith(mac, 41):  # 41=offset in line
            return line.split(' ')[0]
    raise UnknownAddress("'{}' does not have a known ip".format(mac))


# get mac from ip
def get_mac(ip: str) -> str:
    if not verify_ip(ip):
        raise InvalidAddressError("'{}' is not a valid ip address".format(ip))
    f = open('/proc/net/arp', 'r')
    lines = f.readlines()[1:]
    for line in lines:
        if line.startswith(ip, 0):  # 41=offset in line
            return line[41:].split(' ')[0]
    raise UnknownAddress("'{}' does not have a known mac".format(ip))
