all: build run

build:
	sudo docker build -t functiondirector .

run:
	sudo docker run -v function_director_shared:/app/shared functiondirector

create:
	sudo docker create -v function_director_shared:/app/shared --name functiondirector functiondirector

start: create
	sudo docker start functiondirector

config:
	sudo cp /home/$(USER)/.kube/config /var/lib/docker/volumes/function_director_shared/_data/config
