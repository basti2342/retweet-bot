# Retweet Bot follower management module

import common_methods
import logging
import datetime

import tweepy

def manage_followers(api, config):
    """Performs the logic surrounding maintaining active follower using the follower management settings defined in the config file"""

    if config.follower_management['manage_followers'] and common_methods.can_perform_action_today(config.follower_management['days_to_manage']) is True:
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

                if err.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
                    break 

                continue

        print("Finished. %d unfollowed, %d errors." % (unfollowed_count, err_count))    