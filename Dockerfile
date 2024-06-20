# Use the official lightweight Python image.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 10000 available to the world outside this container
EXPOSE 10000

# Ensure the binaries are executable
RUN chmod +x /app/bin/ffmpeg /app/bin/ffplay /app/bin/ffprobe

# Set environment variables
ENV PATH="/app/bin:${PATH}"

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
