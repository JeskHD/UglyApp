#!/bin/bash

set -e

# Update package list
apt-get update

# Install necessary packages
apt-get install -y ffmpeg build-essential

# Install Python dependencies
pip install -r requirements.txt

# Install additional Python packages from GitHub
pip install git+https://github.com/HoloArchivists/twspace_dl.git
