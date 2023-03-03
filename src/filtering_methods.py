"""Retweet Bot filtering module which handles filtering timeline and tweets"""

import logging
from better_profanity import profanity

profanity.load_censor_words()


def filter_status(tweet, query_object):
    """Performs filtering logic on each tweet being processed"""
    filtered_out = []

    if not tweet.retweeted:
        if query_object['filter_profanity'] and profanity.contains_profanity(tweet.text):
            filtered_out.append('profanity')

        if query_object['filter_media'] and tweet.entities['media'] is not None:
            filtered_out.append('contains media')

        if query_object['require_media'] and 'media' in tweet.entities and tweet.entities['media'][0] is None:
            filtered_out.append('no media')

        if query_object['filter_mentions'] and len(tweet.entities['user_mentions']) > 0:
            filtered_out.append('user mention')

        if query_object['max_hashtags'] < len(tweet.entities['hashtags']):
            filtered_out.append('too many hashtags')

        if query_object['max_urls'] < len(tweet.entities['urls']):
            filtered_out.append('too many URLs')

    if filtered_out:
        logging.info(f'Filtered tweet (ID {tweet.id}) due to: {", ".join(filtered_out)}\n')
        return False

    return True


def filter_timeline(timeline, query_object):
    """Performs global filtering on the timeline object returned by Tweepy"""

    blacklist = set(query_object['word_blacklist'])
    user_blacklist = set(query_object['user_blacklist'])

    timeline = [status for status in timeline if not
                any(word in status.text.split() for word in blacklist)]
    timeline = [status for status in timeline if status.author.screen_name not in user_blacklist]

    timeline.reverse()

    return timeline
