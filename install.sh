#!/usr/bin/env bash

# BEFORE STARTING ANYTHING :
# You need to have installed python (v3.7), python-virtualenv, python-pip and pwgen

# Starting strict mode
set -e
set -u
set -o pipefail

# Creating virtual env
python3 -m venv venv

# Sourcing it and installing dependancies
source ./venv/bin/activate
python3 -m pip install -U -r requirements.txt

# Generating conf files
secret_key=$(pwgen -1 -n 100)
sed "s/<generated_random_key>/$secret_key/" langate/langate/settings_local.py.template \
                                            > langate/langate/settings_local.py