


# Build and run Docker image
build:
	# Extract the Git commit hash
	COMMIT_HASH=$(git rev-parse --short HEAD)

	docker build -t image_app:COMMIT_HASH .
	docker run -p 5000:5000 image_app:image_app

# Clean up Docker image and container
clean:
	docker stop image_app
	docker rm image_app
	docker rmi image_name:COMMIT_HASH
