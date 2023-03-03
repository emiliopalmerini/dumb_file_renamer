# set base image
FROM python:3.10-slim-buster

# set the working directory in the container
WORKDIR /app

# copy the requirements file into the container
COPY requirements.txt .

# install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code into the container
COPY . .

# set the command to run when the container starts
CMD ["python", "main.py"]
