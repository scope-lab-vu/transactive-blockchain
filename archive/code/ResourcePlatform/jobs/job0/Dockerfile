#Dockerfile for the task 
# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

ADD matrix.py /

EXPOSE 27017

RUN pip install -r requirements.txt

# Run app.py when the container launches
CMD ["python3", "matrix.py"]
