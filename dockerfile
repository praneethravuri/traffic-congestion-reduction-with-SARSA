# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install dependencies for Pygame
RUN apt-get update && apt-get install -y \
    python3-pygame \
    libsdl2-2.0-0 \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libfreetype6-dev \
    x11-apps

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# CMD instruction is intentionally left out to allow running arbitrary commands
