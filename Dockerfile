# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install git+https://github.com/HoloArchivists/twspace-dl.git

# Make port 10000 available to the world outside this container
EXPOSE 10000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
