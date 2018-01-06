#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import configparser
import hashlib
import inspect
import os

import tweepy

if __name__ == '__main__':
    logging.debug("Bot started")

    PATH = os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe())))

    # read config
    CONFIG = configparser.SafeConfigParser()
    CONFIG.read(os.path.join(PATH, "config"))

    # your hashtag or search query and tweet language (empty = all languages)
    HASHTAG = CONFIG.get("settings", "search_query")
    TWEET_LANG = CONFIG.get("settings", "tweet_language")

    # Number retweets per time
    RATE_LIMIT = int(CONFIG.get("settings", "number_of_rt"))

    # blacklisted users and words
    USER_BLACKLIST = []
    WORD_BLACKLIST = ["RT", u"♺"]

    # build savepoint path + file
    HASHED_HASHTAG = hashlib.md5(HASHTAG.encode('ascii')).hexdigest()
    LAST_FILENAME_ID = "last_id_hashtag_%s" % HASHED_HASHTAG
    BOT_PATH = os.path.dirname(os.path.abspath(__file__))
    LAST_FILE_ID = os.path.join(BOT_PATH, LAST_FILENAME_ID)

    # create bot
    AUTH = tweepy.OAuthHandler(CONFIG.get(
        "twitter", "consumer_key"), CONFIG.get("twitter", "consumer_secret"))
    AUTH.set_access_token(CONFIG.get("twitter", "access_token"),
                          CONFIG.get("twitter", "access_token_secret"))
    API = tweepy.API(AUTH)

    # retrieve last savepoint if available
    try:
        with open(LAST_FILE_ID, "r") as file:
            SAVEPOINT = file.read()
    except IOError:
        SAVEPOINT = ""
        print ("No savepoint found. Bot is now searching for results")

    # search query
    TIMELINE_ITERATOR = tweepy.Cursor(
        API.search, q=HASHTAG, since_id=SAVEPOINT, lang=TWEET_LANG).items(RATE_LIMIT)

    # put everything into a list to be able to sort/filter
    TIMELINE = []
    for status in TIMELINE_ITERATOR:
        TIMELINE.append(status)

    try:
        LAST_TWEET_ID = TIMELINE[0].id
    except IndexError:
        LAST_TWEET_ID = SAVEPOINT

    # filter @replies/blacklisted words & users out and reverse timeline

    # uncomment to remove all tweets with an @mention
    # timeline = filter(lambda status: status.text[0] = "@", timeline)
    TIMELINE = filter(lambda status: not any(word in status.text.split()
                                             for word in WORD_BLACKLIST), TIMELINE)
    TIMELINE = filter(
        lambda status: status.author.screen_name not in USER_BLACKLIST, TIMELINE)
    TIMELINE = list(TIMELINE)
    TIMELINE.reverse()

    TW_COUNT = 0
    ERR_COUNT = 0

    # Iterate the timeline and retweet
    # In case tweet gets deleted in the meantime or already retweeted throw and print error
    for status in TIMELINE:
        try:
            print("(%(date)s) %(name)s: %(message)s\n" %
                  {"date": status.created_at,
                   "name": status.author.screen_name.encode('utf-8'),
                   "message": status.text.encode('utf-8')})

            API.retweet(status.id)
            TW_COUNT += 1
        except tweepy.error.TweepError as err:
            ERR_COUNT += 1
            logging.error(err)
            continue

    print ("Finished. %d Tweets retweeted, %d errors occured." % (TW_COUNT, ERR_COUNT))

    # write last retweeted tweet id to file
    with open(LAST_FILE_ID, "w") as file:
        file.write(str(LAST_TWEET_ID))
