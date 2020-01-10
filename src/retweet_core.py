# Retweet Bot core module

import common_methods
import hashlib
import logging
import tweepy
import re
import os

def filtered_tweet_check(tweet, list_of_previous_tweet_ids, max_hashtags, max_urls, filter_mentions):
    """Filters out retweets, hashtag spamming tweets and @ mentions"""

    find_hashtag_regex = r"#[a-z0-9_]+"
    find_url_regex = r"[localhost|http|https|ftp|file]+://[\w\S(\.|:|/)]+"

    if not tweet.retweeted and tweet.id not in list_of_previous_tweet_ids:

        if filter_mentions and '@' in tweet.text:
            return False

        hashtags_in_tweet = re.finditer(find_hashtag_regex, tweet.text, re.MULTILINE)
        number_of_hashtags_in_tweet = len(list(hashtags_in_tweet))

        if number_of_hashtags_in_tweet >= max_hashtags:
            return False

        urls_in_tweet = re.finditer(find_url_regex, tweet.text, re.MULTILINE)
        number_of_urls_in_tweet = len(list(urls_in_tweet))

        if number_of_urls_in_tweet >= max_urls:
            return False

    return True


def create_hashes_folder():
    """Checks if the hashes directory exists, if not create it"""

    if not os.path.exists('hashes'):
        os.makedirs('hashes')


def get_hashtag_file_id(hashtag):
    """Gets the file id of the passed hashtag"""

    hashed_hashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashed_hashtag
    last_id_file = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'hashes', last_id_filename))

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

def retweet(api, query_objects):
    """Performs the logic surrounding retweeting the query objects defined in the config file"""

    list_of_previous_tweet_ids = []

    for query_object in query_objects:
        if common_methods.can_perform_action_this_month(query_object['months_to_tweet']) is False:
            continue

        if common_methods.can_perform_action_today(query_object['days_to_tweet']) is False:
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
                if filtered_tweet_check(status, list_of_previous_tweet_ids, query_object['max_hashtags'], query_object['max_urls'], query_object['filter_mentions']) is True:
                    print("(%(date)s) %(name)s: %(message)s\n" %
                          {"date": status.created_at,
                           "name": status.author.screen_name.encode('utf-8'),
                           "message": status.text.encode('utf-8')})

                    api.retweet(status.id)
                    list_of_previous_tweet_ids.append(status.id)
                    tweet_count += 1

                    if query_object['favourite_tweets'] is True:
                        api.create_favorite(status.id)

                if query_object['follow_poster'] is True:
                    api.create_friendship(status.author.id)
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
