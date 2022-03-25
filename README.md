# Langate2000

Langate2000 is the captive portal used during the InsaLan esport tournament.

This project has several objectives :

* from the user point of view : be a simple and informative portal during the event.
* from the developer point of view : be easy to maintain and improved (by being modular, having a narrow code base, using simple and tried and tested technologies...).
* from the sysadmin point of view : allow to authenticate and identify the players on the network.

## Configuration

You will need to create a file named `config.py`.
It shall contain the following variables :
* `debug`: if True, both django and netcontrol debug modes will be enabled (do not enable in production)
* `netcontrol_socket_file`: path of the socket file allowing langate and netcontrol to communicate
* `vpn_nb`: number of vpn marks
* `first_mark`: number of first vpn mark
* `django_secret_key`: secret key used by django

### Set the correct games

As games will change from one edition of the festival to another, you will need to modify a few files :
1. In [`langate/portal/models.py`](langate/portal/models.py), change the values of the `Tournament` enum to match the games used for the tournaments :
```
class Tournament(Enum):
    csgo = "Counter Strike Global Offensive"
    tm = "TrackMania 2020"
    lol = "League Of Legends"
```
2. In [`langate/langate/insalan_auth/insalan_backend.py`](langate/langate/insalan_auth/insalan_backend.py), change the content of the `short_name_table` dict. It is used to translate the short names used by the web to values of the eun previously modified, so you should coordinate with the web team to get it right :
```
# Note that the year at the end of the short code is removed
# For example, if the short code is 'CSGO2022', the key in the dict should be 'CSGO'
# This should be changed in the future as it is nothing but a silly way to make mistakes (TODO)
short_name_table = {
	"CSGO": Tournament.csgo,
	"TM": Tournament.tm,
	"lol": Tournament.lol
}
```
3. In [`langate/portal/templates/portal/modal_modify_user.html`](langate/portal/templates/portal/modal_modify_user.html), the lines that look like this :
```
<option value="Tournament.csgo">Counter Strike Global Offensive</option>
<option value="Tournament.tm">TrackMania 2020</option>
<option value="Tournament.lol">League Of Legends</option>
```

## Deployment

### Production

First, you will need to install docker and ipset.

Unlike in the development environment, in the production environment the Dockerfile does not contain the reverse-proxy and the langate2000-netcontrol daemon. These two need to be installed on the host system.

#### nginx

First, install the nginx package provided by your distribution.

Then, we will need to create a configuration file for nginx to be at the same time a reverse proxy in front of the gunicorn server (that lives in the provided docker image) and a static asset server. To do so, create a new file at `/etc/nginx/sites-enabled/portal` following the model below :

```nginx
server { #allow ocsp requests
   listen 80;
   server_name r3.o.lencr.org;

    # si problèmes avec oscp, vérifier la configuration oscp de lets encrypt
    location / {
        proxy_pass http://r3.o.lencr.org;
    }
}

server { #redirect to the portal
    listen 80 default_server;
    return 307 https://gate.insalan.fr/;
}

server {
    listen 443 ssl;
    server_name gate.insalan.fr;

    # here goes all the ssl configuration
    ssl on;
    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.1 TLSv1;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA384 EECDH+ECDSA+SHA256 EECDH+aRSA+SHA384 EECDH+aRSA+SHA256 EECDH+aRSA+RC4 EECDH EDH+aRSA RC4 !aNULL !eNULL !LOW !3DES !MD5 !EXP !PSK !SRP !DSS !RC4";
    
    # reverse proxy redirecting requests to the gunicorn WSGI server
    location / {
        gzip off;

        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # used by the gate to know the IP of the clients on the LAN
        proxy_set_header Host gate.insalan.fr;
        proxy_pass http://127.0.0.1:8000; # gunicorn host and port, if you somehow changed those, you will need to edit this line
    }

    # static assets
    location /static/ {
        alias /var/www/html/static/; # this is the path where the static assets that the gate uses are stored, this path has to exist.
    }

}
```

#### langate2000-netcontrol

launch command `make install` for the first setup of the langate on your computer, that will copy netcontrol.service in systemd.
Then follow the install instructions on the dedicated repository.

#### deploying the web app

Use `make build` to build the production Dockerfile.
This will create a langate docker image.

Then, use `make run` to launch the built image.
The portal should be accessible via the reverse proxy you previously configured.

### Development

First, you will need to install docker.
Then you can build the development Dockerfile by using `make builddev`.
After that, you can launch the built docker image (named `langate-dev`) using `make rundev`.

The portal will be accessible from [http://localhost].
The superuser account's credentials are root/rien.

A `make stopdev` command is also available and will stop the running container and remove the associated image.

## Contributing

The rules are : 
* New features shall be developed in a separate branch and a pull request shall be made when the feature is ready.
* The language used in comments, commits and variables names is english.
* Commit titles shall summurize the update in the least possible number of words (in most cases, try to do 5 words max).
* Small commits are encouraged.
