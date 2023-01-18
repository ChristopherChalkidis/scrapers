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
config_file.set("Other", "gemeenten-text-location", "gemeenten_lite.txt")
config_file.set("Other", "gemeenten-json-location", "gemeenten_names_lite.json")
config_file.set("Other", "gemeenten-links-json-location", "gemeenten_links_lite.json")

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