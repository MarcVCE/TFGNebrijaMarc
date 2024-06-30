# Use an official Python runtime as a parent image 
FROM python:3.12-slim

# Set working directory in the container 
WORKDIR /app 

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copy the requirements file into the container at /app 
COPY requirements.txt . 

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt 

# Copy the rest of the application code into the container at /app 
COPY . . 

# Command to run when the container starts 
CMD [ "python", "main.py" ]
