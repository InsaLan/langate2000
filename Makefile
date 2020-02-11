install:
	cp langate2000-netcontrol.service /etc/systemd/system/

build:
	docker build . -t langate

run:
	systemctl start langate2000-netcontrol
	docker run -itd\
		--privileged -p 8000:8000 \
		--name langate \
		-v /var/www/html/static:/var/www/html/static \
		-v /var/run/langate2000-netcontrol.sock:/var/run/langate2000-netcontrol.sock\
		langate
	docker exec -it langate python3 manage.py collectstatic --noinput

stop:
	docker stop langate
	docker rm langate

restart: stop run

builddev:
	docker build -t langate-dev -f Dockerfile.dev .

rundev:
	docker run -itd --privileged -p 80:80 --name langate-dev langate-dev

stopdev:
	docker stop langate-dev
	docker rm langate-dev
