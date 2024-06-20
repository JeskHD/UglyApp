# Use the official Python image from the Docker Hub
FROM python:3.11.4

# Set the working directory
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
