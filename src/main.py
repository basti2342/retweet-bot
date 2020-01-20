#!/usr/bin/env python
# -*- coding: utf-8 -*-

import common_methods
import retweet_core
import hash_management
import follower_management
import config
import logging


if __name__ == '__main__':
    logging.debug("Bot started")

    CONFIG = config.Config()
    API = retweet_core.api_login(CONFIG.twitter_keys)

    hash_management.create_hashes_folder()

    retweet_core.retweet(API, CONFIG.query_objects)
    
    follower_management.manage_followers(API, CONFIG)