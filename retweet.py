#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import hashlib
import inspect
import json
import re
import os

import tweepy


def filtered_tweet_check(tweet, list_of_previous_tweet_ids, max_hashtags):
    """Filters out retweets, hashtag spamming tweets and @ mentions"""

    find_hashtag_regex = r"(?<=[\s>])#(\d*[A-Za-z_]+\d*)\b(?!;)"

    if not tweet.retweeted and '@' not in tweet.text and tweet.id not in list_of_previous_tweet_ids:

        hashtags_in_tweet = re.finditer(find_hashtag_regex, tweet.text, re.MULTILINE)
        number_of_hashtags_in_tweet = len(list(hashtags_in_tweet))

        if number_of_hashtags_in_tweet <= max_hashtags:
            return True

    return False


def can_perform_action_today(day_to_complete_action):
    """Checks the current day against the day actions should be performed"""

    if datetime.datetime.today().weekday() == day_to_complete_action or day_to_complete_action == 7:
        return True

    return False


def get_hashtag_file_id(hashtag):
    """Gets the file id of the passed hashtag"""

    hashed_hashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashed_hashtag
    rt_bot_path = os.path.dirname(os.path.abspath(__file__))
    last_id_file = os.path.join(rt_bot_path, last_id_filename)

    return last_id_file


def get_hashtag_savepoint(hashtag):
    """Gets the last retweet id of the passed hashtag if it exists"""

    try:
        with open(get_hashtag_file_id(hashtag), "r") as file:
            savepoint = file.read()
    except IOError:
        savepoint = ""
        logging.warning("No savepoint found. Bot is now searching for results")

    return savepoint


def follower_management(api, config):
    """Performs the logic surrounding maintaining active follower using the follower management settings defined in the config file"""

    if config.follower_management['manage_followers'] and can_perform_action_today(config.follower_management['day_to_manage']) is True:
        unfollowed_count = 0
        err_count = 0

        inactivityDate = datetime.date.today() - datetime.timedelta(days = config.follower_management['inactivity_period'])

        followers = API.friends_ids(config.twitter_keys['screen_name'])
        for follower in followers:
            try:
                if (unfollowed_count < config.follower_management['max_unfollows']):
                    lastTweet = API.user_timeline(follower, count = 1)
                    lastTweetDate = lastTweet[0].created_at.date()

                    if lastTweetDate < inactivityDate:
                        API.destroy_friendship(follower)
                        unfollowed_count += 1
                        continue

            except (tweepy.error.TweepError, IndexError) as err:
                err_count += 1
                logging.error(err)   

                if err.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                    break 

                continue

        print("Finished. %d unfollowed, %d errors." % (unfollowed_count, err_count))    


def retweet_logic(api, query_objects):
    """Performs the logic surrounding retweeting the query objects defined in the config file"""

    list_of_previous_tweet_ids = []

    for query_object in query_objects:
        if can_perform_action_today(query_object['day_to_tweet']) is False:
            continue

        savepoint = get_hashtag_savepoint(query_object['search_query'])
        timeline_iterator = tweepy.Cursor(api.search, q=query_object['search_query'], since_id=savepoint,
                                          lang=query_object['tweet_language'], ).items(query_object['tweet_limit'])

        timeline = []
        for status in timeline_iterator:
            timeline.append(status)

        try:
            last_tweet_id = timeline[0].id
        except IndexError:
            last_tweet_id = savepoint

        timeline = filter(lambda status: not any(word in status.text.split()
                                                 for word in query_object['word_blacklist']), timeline)
        timeline = filter(
            lambda status: status.author.screen_name not in query_object['user_blacklist'], timeline)
        timeline = list(timeline)
        timeline.reverse()

        tweet_count = 0
        followed_count = 0
        err_count = 0

        for status in timeline:
            try:
                if filtered_tweet_check(status, list_of_previous_tweet_ids, query_object['max_hashtags']) is True:
                    print("(%(date)s) %(name)s: %(message)s\n" %
                          {"date": status.created_at,
                           "name": status.author.screen_name.encode('utf-8'),
                           "message": status.text.encode('utf-8')})

                    API.retweet(status.id)
                    list_of_previous_tweet_ids.append(status.id)
                    tweet_count += 1

                    if query_object['favourite_tweets'] is True:
                        API.create_favorite(status.id)

                if query_object['follow_poster'] is True:
                    API.create_friendship(status.author.id)
                    followed_count += 1

            except tweepy.error.TweepError as err:
                err_count += 1
                logging.error(err)
                continue

        print("Finished. %d retweeted, %d followed, %d errors." %
              (tweet_count, followed_count, err_count))

        with open(get_hashtag_file_id(query_object['search_query']), "w") as file:
            file.write(str(last_tweet_id))


def api_login(twitter_keys):
    """Logins to the Twitter API using the consumer and access tokens provided in the config file"""

    auth = tweepy.OAuthHandler(
        twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
    auth.set_access_token(
        twitter_keys['access_token'], twitter_keys['access_token_secret'])
    return tweepy.API(auth)


class Config():
    """Attempts to load and set the defined configuration"""

    twitter_keys = {}
    follower_management = {}
    query_objects = {}

    def __init__(self):
        try:
            path = os.path.dirname(os.path.abspath(
                inspect.getfile(inspect.currentframe())))
            with open(os.path.join(path, "config.json")) as json_data_file:
                config_data = json.load(json_data_file)

            self.twitter_keys = config_data['twitter_keys']
            self.follower_management = config_data['follower_management']
            self.query_objects = config_data['query_objects']

        except Exception as err:
            logging.error("Failed to load config. Error: %s", err)


if __name__ == '__main__':
    logging.debug("Bot started")

    CONFIG = Config()
    API = api_login(CONFIG.twitter_keys)

    retweet_logic(API, CONFIG.query_objects)
    follower_management(API, CONFIG)

