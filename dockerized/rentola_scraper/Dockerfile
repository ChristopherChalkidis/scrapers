FROM mcr.microsoft.com/playwright/python:v1.27.1-jammy

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install

WORKDIR /app
COPY . /app

# Run a bash script that contains all scripts that needs to run in order.
CMD ["bash", "scrape_populatedb.sh"]