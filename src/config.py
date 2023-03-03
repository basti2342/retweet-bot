"""Retweet Bot configuration module. Loads the JSON config file into memory.""" 

import logging
import json
import os

class Config():
    """Attempts to load and set the defined configuration"""

    twitter_keys = {}
    follower_management = {}
    query_objects = {}
    general = {}

    def __init__(self):
        try:
            path = os.path.abspath(os.path.join(os.path.dirname( __file__ ),
                                                '..', "config", "config.json"))
            with open(path) as json_data_file:
                config_data = json.load(json_data_file)

            self.twitter_keys = config_data['twitter_keys']
            self.follower_management = config_data['follower_management']
            self.query_objects = config_data['query_objects']
            self.general = config_data['general']

        except Exception as err:
            logging.error("Failed to load config. Error: %s", err)
