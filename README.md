# Scrape funda portal


## A. Getting started
This section helps you get started.
Clone the repo
```
git clone https://github.com/techadvisory/scrapper.git
```
## B. Running instrustion
Before running the script you need to do the following steps:
- step 1 (Install libraries: bs4, selenium, webdriver_manager  )
- step 2 (replace the word "other" in Issue_1.py line 24 with the path that the scrapper folder is in(for me it's gemeenten_file = open(cfg["C://Users//xxx//Documents//git//scrapper"] and      do the same in config_adder.py lines 12, 14, 15, 16)
- Step 3 (Run config_adder.py and then Issue_1.py)

### Running Python modules:
To run `Issue_1.py` run:
```
python Issue_1.py
```

To run `Issue_2.py` and save the results in a sqlite db in the current directory run:
```
python Issue_2.py
```
Same for all the scripts

## File information

* `config_adder` - generates `configurations.ini`
* `Issue_1` - The goal is to use the attached file and verify if the gemeenten (i.e. municipalities) are valid.
    Base URL: https://www.funda.nl/koop/heerhugowaard/1-dag/  replace heerhugowaard with all the entries in the file and verify of the response is 200 

* `Issue_2` -  Creates a python script that:
     iterates over the list of 393 municipalities
     loads the page (e.g. https://www.funda.nl/koop/heerhugowaard/1-dag/ )
     fetches all the URLs that start with https://www.funda.nl/koop/heerhugowaard …

* `Issue_3` -  scrapes to: save new URLs in JSON

* `Issue_5` - Converts municipality into a json file #5

* `gemeenten_names.json` - Contains Gemeenten_names according to places in Json format

* `gemternten_links_20.json` - Contains gemternten links in Json format
