#!/usr/bin/env python3
import sys, json, subprocess, shlex, os
from langate.modules import network

if len(sys.argv) < 2:
    print("Usage : "+__file__+" {start|stop}")
    sys.exit(1)

if sys.argv[1] == "start":
    print("Initializing Ipset & generating Iptables...")

    ipset = network.Ipset(mark=(100,4))
    iptables = ipset.generate_iptables()
    iptables = iptables.split("\n")

    for e in iptables:
        if not e == "" and not e.startswith("#"):
            s = shlex.split(e)
            subprocess.run(s)

    print("Adding whitelisted devices to the set...")

    with open('whitelist.json') as f:
            whitelist = json.load(f)

            for e in whitelist:
                mac = e['mac']
                ipset.connect_user(mac, mark=0)

    print("Launching gunicorn...")
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(curr_dir+"/langate")
    subprocess.run(["gunicorn", "langate.wsgi", "--daemon"])

if sys.argv[1] == "stop":
    
    print("Killing gunicorn")
    subprocess.run(["pkill", "gunicorn"])    

    ipset = network.Ipset(mark=(100,4))

    print("Removing whitelisted devices from the set...")

    with open('whitelist.json') as f:
            whitelist = json.load(f)

            for e in whitelist:
                mac = e['mac']
                ipset.disconnect_user(mac)


    print("Destroying iptables and Ipset")

    iptables = ipset.generate_iptables(stop=True)
    iptables = iptables.split("\n")

    for e in iptables:
        if not e == "" and not e.startswith("#"):
            s = shlex.split(e)
            subprocess.run(s)

    ipset.delete()

