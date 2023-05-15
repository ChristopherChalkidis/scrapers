# Scrape Pararius and Funda

## A. Getting started

This section helps you get started.
Clone the repo

```
git clone https://github.com/techadvisory/scrapper.git
```

## B. How to Run

- I believe these are the steps for a new computer

1. docker build -t scrapers:v1.0 .
2. docker create --name run-scrapers scrapers:v1.0
3. docker compose up

### Scheduled Scrapper
- To spin up a container that will run the scrapper everyday at 8am use
    ```
    cd dockerized
    docker compose up -d
    ```
  - The `-d` flag will run it in the background. 
  - The scrapped data and database file will be stored in docker volumes `dockerized_funda-listings` and `dockerized_funda-database` respectively.


- To stop and remove the containers, make sure you're in the `dockerized` directory and run
    ```
    docker compose down
    ```
  - To remove the volumes as well, add the flag `-v` to the command above.

- At any time you can check the container/s currently running by using `docker ps`


