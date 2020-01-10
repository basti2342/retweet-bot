# Retweet Bot follower management module

import common_methods
import logging
import datetime

import tweepy

def manage_followers(api, config):
    """Performs the logic surrounding maintaining active follower using the follower management settings defined in the config file"""

    if (config.follower_management['manage_followers'] and
        common_methods.can_perform_action_today(config.follower_management['days_to_manage']) is True and
        common_methods.can_perform_action_this_month(config.follower_management['months_to_manage']) is True):
        
        if config.follower_management['aggressive_management'] is True:
            aggressive_management(api, config)
        else:
            passive_management(api, config)


def aggressive_management(api, config):
    """Aggressive management unfollows any followers until rate limit is hit that aren't following back"""

    limit_hit = False
    unfollowed_count = 0
    err_count = 0

    try:
        for page in tweepy.Cursor(api.friends, count = 100).pages():  
            if limit_hit is False:      
                user_ids = [user.id for user in page]

                for user in api._lookup_friendships(user_ids):
                    try:
                        if (unfollowed_count > config.follower_management['max_unfollows']):
                            limit_hit = True
                            break

                        if not user.is_followed_by:
                            api.destroy_friendship(user.id)
                            unfollowed_count += 1

                    except (tweepy.error.TweepError, IndexError) as err:
                        err_count += 1
                        logging.error(err)   

                        if (hasattr(err, 'reason')):
                            if err.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                                limit_hit = True
                                break 

                        continue

    except (tweepy.error.TweepError, IndexError) as err:
        err_count += 1
        logging.error(err)   

        if (hasattr(err, 'reason')):
            if err.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                limit_hit = True

    print("Finished. %d unfollowed, %d errors." % (unfollowed_count, err_count))


def passive_management(api, config):
    """Passive management unfollows any followers who haven't tweeted within the inactivity date set in config"""

    unfollowed_count = 0
    err_count = 0

    inactivityDate = datetime.date.today() - datetime.timedelta(days = config.follower_management['inactivity_period'])

    followers = api.friends_ids(config.twitter_keys['screen_name'])
    for follower in followers:
        try:
            if (unfollowed_count < config.follower_management['max_unfollows']):
                lastTweet = api.user_timeline(follower, count = 1)
                lastTweetDate = lastTweet[0].created_at.date()

                if lastTweetDate < inactivityDate:
                    api.destroy_friendship(follower)
                    unfollowed_count += 1
                    continue

        except (tweepy.error.TweepError, IndexError) as err:
            err_count += 1
            logging.error(err)   

            if (hasattr(err, 'reason')):
                if err.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                    break 

            continue

    print("Finished. %d unfollowed, %d errors." % (unfollowed_count, err_count))
