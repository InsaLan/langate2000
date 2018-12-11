#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
from typing import Dict, Set, List, Tuple
from time import time
from subprocess import run, PIPE, TimeoutExpired
from random import randint
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
    """permission request timed out or was denied, verify /etc/sudoers ?"""


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
    #name: str
    #counter: bool
    #skbinfo: bool
    #mark_start: int
    #mark_mod: int
    #next_add: int
    #multi_vpn_mark: int
    #user_logs: List[Tuple[time, Dict[str, (int, int)]]]
    #vpn_logs: List[Tuple[time, Dict[int, (int, int)]]]
    #last_user_measure: Dict[str, (int,int)]
    #last_vpn_measure: Dict[int, (int,int)]

    def __init__(self, name="langate", default_timeout=0, counter=True, marking=True, mark=(0, 1),
                 multi_vpn_mark=4294967295, fixed_vpn_timeout=30):
        """
        Create a new set with provided arguments. Equivalent to the command :
        'sudo ipset create langate hash:mac -exist hashsize 4096 timeout 0 counters skbinfo"

        :param name: Name of the set.
        :param default_timeout: Timeout by default.
        :param counter: Enable bandwith counters
        :param marking: Enable packet marking
        :param mark: First mark and number of mark to use. Useless if marking=False
        :param multi_vpn_mark: Mark for devices mapped to multiple marks. Useless if marking=False
        :param fixed_vpn_timeout: Number of seconds without network usage before a user may change of vpn
        """
        self.name = name
        self.timeout = default_timeout
        self.counter = counter
        self.skbinfo = marking
        (self.mark_start, self.mark_mod) = mark
        self.next_add = 0
        self.multi_vpn_mark = multi_vpn_mark
        if self.counter:
            self.user_logs = list()
            self.last_user_measure = defaultdict(lambda: [0,0], {})
            if self.skbinfo:
                self.vpn_logs = list()
                self.last_vpn_measure = defaultdict(lambda: [0,0], {})
        creation_args = ["sudo", "ipset", "create", self.name, "hash:mac",
                         "-exist", "hashsize", "4096", "timeout", str(default_timeout)]
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
        if self.counter:
            creation_args = ["sudo", "ipset", "create", self.name + "-download" , "hash:mac",
                             "-exist", "hashsize", "4096", "timeout", str(default_timeout), "counters"]
            result = run(creation_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise UnknownInitializationError(result.stderr.decode("UTF-8"))
        if self.counter and self.skbinfo:
            # CMD=sudo ipset create langate-recent hash:mac -exist hashsize 4096 timeout 60
            creation_args = ["sudo", "ipset", "create", self.name + "-recent", "hash:mac", "-exist", "hashsize", "4096",
                             "timeout", str(fixed_vpn_timeout)]
            result = run(creation_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise UnknownInitializationError(result.stderr.decode("UTF-8"))

    def generate_iptables(self, match_internal: str = "-s 172.16.0.0/255.252.0.0", stop: bool = False) -> str:
        """
        def __init__(self, name="langate", default_timeout=0, counter=True, marking=True, mark=(0, 1),
                     multi_vpn_mark=4294967295, fixed_vpn_timeout=30):
        """
        if stop:
            A="D"
        else:
            A="A"
        res = "# Portal rules :\n"
        res+= "iptables -" + A + " FORWARD " + match_internal + " -m set ! --match-set " + self.name + " src ! --update-counters -j REJECT\n"
        res+= "iptables -t nat -" + A + " PREROUTING " + match_internal + " -p tcp --dport 80 -m set ! --match-set " + self.name + " src ! --update-counters -j REDIRECT --to-ports 80\n"
        res+= "\n\n# Marking and accounting rules\n"
        # accounting is done automatically when no ! --update-counters is provided
        res+= "iptables -t mangle -" + A + " FORWARD -m set --match-set " + self.name + " src ! --update-counters -j SET --map-set " + self.name + " src --map-mark\n"
        res+= "iptables -t mangle -" + A + " FORWARD -m set --match-set " + self.name + " src -j SET --add-set " + self.name + "-recent src --exist\n"
        res+= "iptables -t mangle -" + A + " FORWARD -m set --match-set " + self.name + "-download dst -j SET --add-set " + self.name + "-recent dst --exist\n"
        res+= "\n\n# Map single device to any number of vpns\n"
        res+= "iptables -t mangle -" + A + " FORWARD -m mark --mark " + str(self.multi_vpn_mark) + " -j HMARK --hmark-tuple src,dst,sport,dport "
        res+= "--hmark-offset " + str(self.mark_start) + " --hmark-mod " + str(self.mark_mod) + " --hmark-rnd " + str(randint(0, 2**32))
        return res

    def connect_user(self, mac: str, timeout: int = None, mark: int = None, counter: Tuple[int,int] = (0,0), multi_vpn: bool = False):
        """
        Add a user to the set.
        Equivalent to the command :
        'sudo ipset add langate 00:00:00:00:00:01 -exist timeout 0 skbmark 0'

        :param mac: Mac of the user.
        :param timeout: (Optional) Timeout after which the user will be disconnected.
        :param mark: Mark to use for this entry, None for automatic
        :param counter: Value to initialize bandwith counter to
        :param multi_vpn: True if device should be mapped to multiple vpn (caching server...)
        """

        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        connect_args = ["sudo", "ipset", "add", self.name, mac, "-exist"]
        if timeout is not None:
            connect_args.append("timeout")
            connect_args.append(str(timeout))
        if self.counter:
            connect_args.append("bytes")
            connect_args.append(str(counter[1]))
        elif counter != 0:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        if self.skbinfo:
            connect_args.append("skbmark")
            if multi_vpn:
                connect_args.append(hex(self.multi_vpn_mark))
            elif mark is None:
                connect_args.append(hex(self.next_add + self.mark_start))
                self.next_add = (self.next_add + 1) % self.mark_mod
            else:
                connect_args.append(hex(mark))
        elif mark is not None:
            raise FeatureDisabledError("Feature skbinfo is disabled for this set")
        result = run(connect_args, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

        if self.counter:
            connect_args = ["sudo", "ipset", "add", self.name + "-download", mac, "-exist"]
            if timeout is not None:
                connect_args.append("timeout")
                connect_args.append(str(timeout))
            connect_args.append("bytes")
            connect_args.append(str(counter[0]))
            result = run(connect_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))

    def disconnect_user(self, mac: str):
        """
        Remove a user from the set.
        Equivalent to the command :
        'sudo ipset del langate 00:00:00:00:00:01'

        :param mac: Mac of the user.
        """
        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))
        disconnect_args = ["sudo", "ipset", "del", self.name, mac, "-exist"]
        result = run(disconnect_args, stderr=PIPE, timeout=2)

        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))

        if self.counter:
            disconnect_args = ["sudo", "ipset", "del", self.name + "-download", mac, "-exist"]
            result = run(disconnect_args, stderr=PIPE, timeout=2)

    def get_user_info(self, mac: str) -> (bool, (int, int), int):
        """
        Get users information from his mac address.
        Obtained by the commands :
        'sudo ipset test langate 00:00:00:00:00:01 -q'
        and 'sudo ipset list langate | grep 00:00:00:00:00:01'

        :param mac: Mac adress of the user.
        :return: (bool:1, (int:2,int:3) ,int:4) with
        1 : if the user is connected,
        2 : how much bytes were transfered in download
        3 : how much bytes were transfered in upload
        and 4 : what mark is used for the entry.
        """

        if not verify_mac(mac):
            raise InvalidAddressError("'{}' is not a valid mac address".format(mac))

        test_args = ["sudo", "ipset", "test", self.name, mac, "-q"]

        result = run(test_args, timeout=2)

        if result.returncode != 0:
            return False, (0,0), 0
        if not self.counter and not self.skbinfo:
            return True, (0,0), 0

        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        res = (None, None, None)
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
                res = (True, byte, skbmark)
        if self.counter:
            list_args = ["sudo", "ipset", "list", self.name + "-download"]
            result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))
            out = result.stdout.decode("UTF-8")
            down = None
            for line in out.splitlines():
                if re.match(mac.upper() + '.*', line):
                    byte = re.search('bytes ([0-9]+)', line)
                    if byte:
                        down = int(byte.group(1))
                    else:
                        down = 0
            full_res = (res[0], (down, res[1]), res[2])
        else:
            full_res = (res[0], (None, res[1]), res[2])
        return full_res

    def clear(self):
        """
        Clear the set, by removing all entry from it. Equivalent to the command :
        'sudo ipset flush langate'
        """
        clear_args = ["sudo", "ipset", "flush", self.name]
        result = run(clear_args, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        if self.counter:
            clear_args = ["sudo", "ipset", "flush", self.name + "-download"]
            result = run(clear_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))


    def get_all_connected(self) -> Dict[str, Tuple[Tuple[int, int], int]]:
        """
        Get all entries from the set, with how much bytes they transferred and what is their mark.
        Equivalent to the command : 'sudo ipset list langate"

        :return: Dictionary mapping device MAC to their bandwith usage (down and up) and mark
        """
        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out = result.stdout.decode("UTF-8")
        res = dict()
        for line in out.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search('(([0-9A-F]{2}:){5}[0-9A−F]{2})', line).group(1)
                byte = re.search(r'bytes ([0-9]+)', line)
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
        if self.counter:
            list_args = ["sudo", "ipset", "list", self.name + "-download"]
            result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))
            out = result.stdout.decode("UTF-8")
            full_res = dict()
            for line in out.splitlines():
                if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                    mac = re.search('(([0-9A-F]{2}:){5}[0-9A−F]{2})', line).group(1)
                    byte = re.search(r'bytes ([0-9]+)', line)
                    if byte:
                        byte = int(byte.group(1))
                    else:
                        byte = 0
                    full_res[mac] = ((byte, res[mac][0]), res[mac][1])
        else:
            full_res = dict()
            for k in res:
                full_res[k] = ((0, res[mac][0]), res[mac][1])
        return res

    def delete(self):
        """
        Delete the set. Equivalent to the command :
        'sudo ipset destroy langate"
        """
        clear_args = ["sudo", "ipset", "destroy", self.name]
        result = run(clear_args, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        if self.counter:
            clear_args = ["sudo", "ipset", "destroy", self.name + "-download"]
            result = run(clear_args, stderr=PIPE, timeout=2)
            if result.returncode != 0:
                raise GenericNetworkError(result.stderr.decode("UTF-8"))


    # add an entry to internal log
    def log_statistics(self):
        """
        Add an entry to internal log. Equivalent to the command :
        'sudo ipset list langate'
        """

        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")

        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out_u = result.stdout.decode("UTF-8")
        list_args = ["sudo", "ipset", "list", self.name]
        result = run(list_args, stdout=PIPE, stderr=PIPE, timeout=2)
        if result.returncode != 0:
            raise GenericNetworkError(result.stderr.decode("UTF-8"))
        out_d = result.stdout.decode("UTF-8")
        current_time = time()
        user_log = defaultdict(lambda: [0,0], {})
        if self.skbinfo:
            vpn_log = defaultdict(lambda: [0,0], {})
        for line in out_u.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = int(re.search('bytes ([0-9]+)', line).group(1))

                if mac in self.last_user_measure:
                    user_log[mac][1] = byte - self.last_user_measure[mac][1]
                else:
                    user_log[mac][1] = byte
                self.last_user_measure[mac][1] = byte
                if self.skbinfo:
                    vpn = re.search('skbmark (0x[0-9]+)', line)
                    if vpn:
                        vpn = int(vpn.group(1), 16)
                        user_log[mac][0] = vpn
                    else:
                        continue
                    vpn_log[vpn][1] += byte

        for line in out_d.splitlines():
            if re.match('([0-9A-F]{2}:){5}[0-9A−F]{2}.*', line):
                mac = re.search("(([0-9A-F]{2}:){5}[0-9A−F]{2})", line).group(1)
                byte = int(re.search('bytes ([0-9]+)', line).group(1))

                if self.skbinfo:
                    vpn_log[user_log[mac][0]][0] += byte
                if mac in self.last_user_measure:
                    user_log[mac][0] = byte - self.last_user_measure[mac][0]
                else:
                    user_log[mac][0] = byte
                self.last_user_measure[mac][0] = byte

        #user_logs: List[Tuple[time, Dict[str, (int, int)]]]
        self.user_logs.append((current_time, user_log))

        if self.skbinfo:
            for vpn in vpn_log:
                vpn_log[vpn][0] -= self.last_vpn_measure[vpn][0]
                vpn_log[vpn][1] -= self.last_vpn_measure[vpn][1]
                self.last_vpn_measure[vpn][0] += vpn_log[vpn][0]
                self.last_vpn_measure[vpn][1] += vpn_log[vpn][1]
            self.vpn_logs.append((current_time, vpn_log))

    def get_users_logs(self) -> List[Tuple[time, Dict[str, Tuple[int, int]]]]:
        """
        Get logs by users, sorted by date.

        :return: List sorted by date of tuple of date and dictionary, itself mapping device's
        Mac to it's bandwith usage since last entry
        """
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        return self.user_logs

    def get_vpn_logs(self) -> List[Tuple[time, Dict[int, Tuple[int, int]]]]:
        """
        Get logs by vpn sorted by date.

        :return: List sorted by date of tuple of date and dictionary, itself mapping vpn mark
        to it's bandwith usage since last entry
        """
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        if not self.skbinfo:
            raise FeatureDisabledError("Feature skbinfo is disabled for this set")
        return self.vpn_logs

    def clear_logs(self, after=time()):
        """
        Clear internal logs (logs are never cleared otherwise, taking memory indefinitely).

        :param after: Time after which the cleaning must be done, now if not set.
        """
        if not self.counter:
            raise FeatureDisabledError("Feature counter is disabled for this set")
        lo = 0
        hi = len(self.user_logs)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.user_logs[mid][0] < after:
                lo = mid + 1
            else:
                hi = mid
        index = lo
        self.user_logs = self.user_logs[index:]
        if self.skbinfo:
            self.vpn_logs = self.vpn_logs[index:]

    def try_balance(self):
        """
        Try to auto-balance vpn usage by switching some user of vpn.
        """

        if self.counter and self.skbinfo:
            # get users recent network usage
            logs = self.get_users_logs()
            if len(logs) > 0:
                log = logs[-1][1][0] + logs[-1][1][1]
            else:
                return
            user_info = self.get_all_connected()
            all_connected = set(user_info)

            # get all fixed users
            list_args = ["sudo", "ipset", "list", self.name + "-recent"]
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
                self.set_vpn(player, vpn[0])
                vpn = sorted(vpn, key=lambda v: vpn_usage[v])

        else:
            raise FeatureDisabledError("Feature counter or skbinfo is disabled for this set")

    def get_balance(self) -> Dict[int, Set[str]]:
        """
        Get current mapping of vpn and mac (each entry contain the vpn number, with who is connected to it)

        :return: Dictionary composed of vpn and set of mac addresses
        """
        res = dict()
        connected = self.get_all_connected()
        for mac in connected:
            if connected[mac][1] in res:
                res[connected[mac][1]].add(mac)
            else:
                res[connected[mac][1]] = set()
                res[connected[mac][1]].add(mac)
        return res

    def set_vpn(self, mac: str, vpn: int):
        """
        Move an user to a new vpn.

        :param mac: Mac address of the user.
        :param vpn: Vpn where move the user to.
        """
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
                self.last_vpn_measure[old_vpn][0] = self.last_vpn_measure[old_vpn][0] \
                                                 - self.last_user_measure[mac][0]
                self.last_vpn_measure[old_vpn][1] = self.last_vpn_measure[old_vpn][1] \
                                                 - self.last_user_measure[mac][1]
                self.last_vpn_measure[vpn][0] = self.last_vpn_measure[vpn][0] \
                                             + self.last_user_measure[mac][0]
                self.last_vpn_measure[vpn][1] = self.last_vpn_measure[vpn][1] \
                                             + self.last_user_measure[mac][1]
        else:
            raise NotInSetError("'{}' is not in the set")


def verify_mac(mac: str) -> bool:
    """
    Verify if mac address is correctly formed.

    :param mac: Mac address to verify.
    :return: True is correctly formed, False if not.
    """
    return bool(re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac))


def verify_ip(ip: str) -> bool:
    """
    Verify if ip address is correctly formed.

    :param ip: Ip address to verify.
    :return: True is correctly formed, False if not.
    """
    return bool(re.match(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$', ip))


def get_ip(mac: str) -> str:
    """
    Get the ip address associated with a given mac address.

    :param mac: Mac address of the user.
    :return: Ip address of the user.
    """
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
    """
    Get the mac address associated with a given ip address.

    :param ip: Ip address of the user.
    :return: Mac address of the user.
    """
    if not verify_ip(ip):
        raise InvalidAddressError("'{}' is not a valid ip address".format(ip))
    f = open('/proc/net/arp', 'r')
    lines = f.readlines()[1:]
    for line in lines:
        if line.startswith(ip, 0):  # 41=offset in line
            return line[41:].split(' ')[0]
    raise UnknownAddress("'{}' does not have a known mac".format(ip))
