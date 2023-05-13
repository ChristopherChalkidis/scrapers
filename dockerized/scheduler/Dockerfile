FROM docker:dind

COPY crontab .
RUN mkdir /logs

CMD crontab crontab && crond -f