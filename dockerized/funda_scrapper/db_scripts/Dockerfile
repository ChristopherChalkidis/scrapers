FROM python:3.10-slim-buster

WORKDIR /db_scripts

COPY . /db_scripts

RUN mkdir /database /listings

CMD [ "bash","/db_scripts/start_populate_db.sh" ]