# Use an official Python runtime as a parent image
FROM python:2.7-slim

# Set the working directory to /app
# and copy the local contents into the container at /app
WORKDIR /app
ADD ./src /app/src
ADD ./config /app/config
ADD ./requirements.txt /app/requirements.txt

RUN mkdir -p /app/logs
RUN touch /app/logs/mylog.log

# Install dependencies
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000
EXPOSE 27017


# Run app when de container launches
ENTRYPOINT ["/usr/local/bin/gunicorn", "--log-config", "config/logging.conf", "-b", ":8000", "src.main.wsgi"]
