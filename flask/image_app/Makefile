


# Build and run Docker image
build:
	# Extract the Git commit hash
	COMMIT_HASH=$(git rev-parse --short HEAD)

	docker build -t image_app:COMMIT_HASH .
	
run:
	docker run -ti --runtime=nvidia -e NVIDIA_DRIVER_CAPABILITIES=compute,utility -e NVIDIA_VISIBLE_DEVICES=all --network host -p 5000:5000 image_app

# Clean up Docker image and container
clean:
	docker stop image_app
	docker rm image_app
	docker rmi image_app:COMMIT_HASH
