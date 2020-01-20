# Retweet Bot filtering module which handles filtering timeline and statuses based on query_objects


def filter_status(tweet, list_of_previous_tweet_ids, max_hashtags, max_urls, filter_mentions, filter_media):
    """Performs filtering logic on each tweet being processed"""

    if not tweet.retweeted or tweet.id not in list_of_previous_tweet_ids:

        if filter_media and tweet.entities['media'] is not None:
            return False

        if filter_mentions and len(tweet.entities['user_mentions']) > 0:
            return False
            
        if max_hashtags < len(tweet.entities['hashtags']):
            return False

        if max_urls < len(tweet.entities['urls']):
            return False

    return True
    
def filter_timeline(timeline, query_object):
    """Performs global filtering on the timeline object returned by Tweepy"""

    timeline = filter(lambda status: not any(word in status.text.split()
                                                for word in query_object['word_blacklist']), timeline)
    timeline = filter(
        lambda status: status.author.screen_name not in query_object['user_blacklist'], timeline)
    
    timeline = list(timeline)
    timeline.reverse()

    return timeline