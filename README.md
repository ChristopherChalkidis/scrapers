# Scrape Pararius and Funda

## A. Getting started

This section helps you get started.
Clone the repo

```
git clone https://github.com/techadvisory/scrapper.git
```

## B. Scheduled Scrapper
- To spin up a container that will run the scrapper everyday at 8am use
    ```
    cd dockerized
    docker compose up -d
    ```
  - The `-d` flag will run it in the background. 
  - The scrapped data and database file will be stored in docker volumes `dockerized_funda-listings`, `dockerized_pararius_listings` and `dockerized_funda-database`, `dockerized_pararius_database` respectively.


- To stop and remove the containers, make sure you're in the `dockerized` directory and run
    ```
    docker compose down
    ```
  - To remove the volumes as well, add the flag `-v` to the command above.

- At any time you can check the container/s currently running by using `docker ps`


