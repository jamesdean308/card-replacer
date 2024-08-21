# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Copy and run entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Define environment variable
ENV FLASK_APP=run.py

# Run the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]
