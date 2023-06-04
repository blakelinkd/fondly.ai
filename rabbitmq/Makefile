IMAGE_NAME = rabbitmq-image
CONTAINER_NAME = rabbitmq-server

.PHONY: build run clean

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -d --name $(CONTAINER_NAME) -p 5672:5672 -p 15672:15672 $(IMAGE_NAME)

clean:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)
	docker rmi $(IMAGE_NAME)
