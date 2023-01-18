"""
Issue #6

scrapper: move configurations to a config file
"""
import configparser


# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('configurations.ini')
    return config
