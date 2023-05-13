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

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser
RUN mkdir /app/listings /app/database
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

# Run a bash script that contains all scripts that needs to run in order.
CMD [ "bash","/app/scrape_populatedb.sh" ]
