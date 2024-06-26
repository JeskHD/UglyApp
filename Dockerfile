# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir git+https://github.com/HoloArchivists/twspace_dl.git

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run gunicorn server when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "600", "--log-level", "debug", "app:app"]
