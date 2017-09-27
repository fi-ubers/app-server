# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
# and copy the local contents into the container at /app
WORKDIR /app
ADD . /app

RUN mkdir -p /app/logs
RUN touch /app/logs/mylog.log

# Install dependencies
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
EXPOSE 27017

# Define environment variables with
# ENV MONGODB_URL "mongodb://juanfresia:testdb@ds123534.mlab.com:23534/fiuber-app-server-testdb"
# ENV VARIABLE value

# Run app when de container launches
ENTRYPOINT ["/usr/local/bin/gunicorn", "--log-config", "config/logging.conf", "-b", ":8000", "src.main.wsgi"]
