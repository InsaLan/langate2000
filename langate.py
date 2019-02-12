#!/usr/bin/env python3
import sys, json, subprocess, shlex, os
from langate.modules import network

def do_iptables(stop=False):

    iptables = ipset.generate_iptables(stop=stop)
    iptables = iptables.split("\n")

    for e in iptables:
        if not e == "" and not e.startswith("#"):
            s = shlex.split(e)
            subprocess.run(s)

def do_whitelist(stop=False):

    connected_devices = ipset.get_all_connected().keys()

    if os.path.isfile("whitelist.json"):

        with open('whitelist.json') as f:
                whitelist = json.load(f)

                for e in whitelist:
                    mac = e['mac']

                    if mac not in connected_devices:
                        if stop:
                            ipset.disconnect_user(mac)
                        else:
                            ipset.connect_user(mac, mark=0)
    else:
        print("\nWarning: there is no whitelist.json file in this folder,\n"+
              "The whitelist.json file contains the mac addresses of all devices that can access the internet without having to log into the langate.\n"+
              "You may want to add one to whitelist all your servers...\n")


if len(sys.argv) < 2 or sys.argv[1] not in ["start", "stop", "whitelist_reload"]:
    print("Usage : "+__file__+" {start|stop|whitelist_reload}")
    sys.exit(1)

print("Loading Ipset...")
ipset = network.Ipset(mark=(100,4))

if sys.argv[1] == "start":
    print("Generating Iptables...")

    do_iptables(stop=False)

    print("Adding whitelisted devices to the set...")

    do_whitelist(stop=False)

    print("Launching gunicorn...")
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(curr_dir+"/langate")
    subprocess.run(["gunicorn", "langate.wsgi", "--daemon"])

if sys.argv[1] == "stop":
    
    print("Killing gunicorn")
    subprocess.run(["pkill", "gunicorn"])

    print("Removing whitelisted devices from the set...")

    do_whitelist(stop=True)

    print("Destroying iptables")

    do_iptables(stop=True)

    ipset.delete()

if sys.argv[1] == "whitelist_reload":
    print("Reloading the whitelist...")
    do_whitelist(stop=False)