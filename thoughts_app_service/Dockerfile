# Use the official Python image from the Docker Hub
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

# Add the current directory . in the project to the working directory /code
COPY . /code/

RUN chmod +x /code/initialize_db.sh

# Set the command to run the entrypoint script
CMD ["/code/initialize_db.sh"]