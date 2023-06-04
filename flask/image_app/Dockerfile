# Base image
FROM nvidia/cuda:11.2.1-runtime-ubuntu20.04

# Install NVIDIA Container Toolkit dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && apt-get clean

# Add the NVIDIA CUDA repository and GPG key
RUN curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
RUN distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && \
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Container Toolkit
RUN apt-get update && apt-get install -y \
    nvidia-container-toolkit \
    && apt-get clean

# Install Python and other necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean

# Set the working directory
WORKDIR /image_app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Flask app files
COPY . .

# Expose the port on which the Flask app will run (replace 5000 with the appropriate port if needed)
EXPOSE 5000

# Run the Flask app
CMD ["python3", "image_app.py"]
