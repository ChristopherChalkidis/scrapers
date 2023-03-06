"""
Issue #6

scrapper: move configurations to a config file
"""
import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD Other SECTION
config_file.add_section("Other")
# ADD SETTINGS TO Other SECTION
# Leave the following as is, and it will create the configurations for the normal files.
# gemeenten-text-location -> Text file containing all 393 municipality names.
config_file.set("Other", "gemeenten-text-location", "gemeenten.txt")
# gemeenten-json-location -> Json file containing all 393 municipality names in Json format.
config_file.set("Other", "gemeenten-json-location", "gemeenten_names.json")
# gemeenten-links-json-location -> Json file containing the links that were scrapped in the last 24 hours.
config_file.set("Other", "gemeenten-links-json-location", "gemeenten_links.json")

config_file.set("Other", "gemeenten-json-names-pararius", "gemeenten_names_pararius.json")

config_file.set("Other", "gemeenten-json-links-pararius", "gemeenten_links_pararius.json")

# SAVE CONFIG FILE
with open(r"configurations.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'configurations.ini' created")

# PRINT FILE CONTENT
read_file = open("configurations.ini", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()