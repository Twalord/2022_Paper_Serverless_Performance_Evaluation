all: build push

registry_url = YOUR URL HERE

build:
	sudo docker build -t $(registry_url)/nuclio-magick-np .

push:
	sudo docker push $(registry_url)/nuclio-magick-np
