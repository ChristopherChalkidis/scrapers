# For more information, please refer to https://aka.ms/vscode-docker-python
FROM mcr.microsoft.com/playwright/python:v1.27.1-jammy

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
#RUN playwright install

WORKDIR /app
COPY . /app

RUN mkdir listings database

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#This should point at and start the bash scheduling script
CMD ["python3", "funda_get_daily.py"] 

# Database dockerfile
# FROM python:3.10-slim-buster

# WORKDIR /db_scripts

# COPY . /db_scripts

# RUN mkdir /database /listings

CMD [ "bash","/db_scripts/start_populate_db.sh" ]
