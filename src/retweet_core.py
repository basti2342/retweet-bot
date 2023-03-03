"""Retweet Bot core module"""

import logging
import tweepy
import hash_management
import filtering_methods
import common_methods


async def retweet(api, query_objects):
    """Performs the logic surrounding retweeting the query objects defined in the config file"""

    list_of_previous_tweet_ids = []

    for query_object in query_objects:
        if common_methods.can_perform_action_this_month(query_object['months_to_tweet']) is False:
            continue

        if common_methods.can_perform_action_today(query_object['days_to_tweet']) is False:
            continue

        savepoint = hash_management.get_hash_savepoint(query_object['search_query'])
        timeline_iterator = tweepy.Cursor(api.search,
                                          q=query_object['search_query'],
                                          since_id=savepoint,
                                          lang=query_object['tweet_language']
                                          ).items(query_object['tweet_limit'])

        timeline = []
        for status in timeline_iterator:
            timeline.append(status)

        try:
            last_tweet_id = timeline[0].id
        except IndexError:
            last_tweet_id = savepoint

        timeline = filtering_methods.filter_timeline(timeline, query_object)

        tweet_count = 0
        followed_count = 0
        err_count = 0
        favourite_count = 0
        can_follow = True

        for status in timeline:
            try:
                if status.id in list_of_previous_tweet_ids:
                    continue
                else:
                    list_of_previous_tweet_ids.append(status.id)

                if filtering_methods.filter_status(status, query_object) is True:

                    logging.info("(%(date)s) %(name)s: %(message)s\n" %
                          {"date": status.created_at,
                           "name": status.author.screen_name.encode('utf-8'),
                           "message": status.text.encode('utf-8')})

                    if query_object['retweet'] is True:
                        api.retweet(status.id)
                        tweet_count += 1

                    if query_object['favourite_tweets'] is True:
                        api.create_favorite(status.id)
                        favourite_count += 1

                    if query_object['follow_poster'] is True and can_follow is True:
                        api.create_friendship(status.author.id)
                        followed_count += 1

            except tweepy.RateLimitError as err:
                logging.error("Hit rate limit, breaking out of current process. Error: %d", err)
                err_count += 1
                break
            except tweepy.TweepError as err:
                error_code = err.response.json()['errors'][0]['code']
                if error_code == 161:
                    logging.error("Unable to follow more people at this time.")
                    can_follow = False
                    err_count += 1
                    continue

        logging.info("Finished. %d retweeted, %d followed, %d favourited, %d errors.\n",
              tweet_count, followed_count, favourite_count, err_count)

        with open(hash_management.get_hash_file_id(query_object['search_query']), "w") as file:
            file.write(str(last_tweet_id))


def api_login(twitter_keys):
    """Logins to the Twitter API using the consumer and access tokens provided in the config file"""

    auth = tweepy.OAuthHandler(
        twitter_keys['consumer_key'], twitter_keys['consumer_secret'])
    auth.set_access_token(
        twitter_keys['access_token'], twitter_keys['access_token_secret'])
    return tweepy.API(auth)
