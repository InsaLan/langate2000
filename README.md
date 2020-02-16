# Langate2000

Langate2000 is the captive portal used during the InsaLan esport tournament.

This project has several objectives :

* from the user point of view : be a simple and informative portal during the event.
* from the developer point of view : be easy to maintain and improved (by being modular, having a narrow code base, using simple and tried and tested technologies...).
* from the sysadmin point of view : allow to authenticate and identify the players on the network.

## Deployment

### Production

First, you will need to install docker and ipset.

Unlike in the development environment, in the production environment the Dockerfile does not contain the reverse-proxy and the langate2000-netcontrol daemon. These two need to be installed on the host system.

#### nginx

First, install the nginx package provided by your distribution.

Then, we will need to create a configuration file for nginx to be at the same time a reverse proxy in front of the gunicorn server (that lives in the provided docker image) and a static asset server. To do so, create a new file at `/etc/nginx/sites-enabled/portal` following the model below :

```nginx
# Optional portal redirection http -> https
server {
  listen 80 default_server;
  return 307 https://gate.insalan.fr/;
}

server {
  listen 443 ssl;
  server_name gate.insalan.fr;
  
  ssl on;
  
  # here goes all the ssl configuration
  
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

Follow the install instructions on the dedicated repository.

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
