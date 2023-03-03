"""Retweet Bot follower management module."""

import concurrent.futures
import logging
import datetime
import tweepy
import common_methods
from tweepy_logging import log_errors


async def manage_followers(api, config):
    """Performs logic maintaining active followers using the settings defined in the config file"""

    if (config.follower_management['manage_followers'] and
        common_methods.can_perform_action_today(config.follower_management['days_to_manage'])
        is True and
        common_methods.can_perform_action_this_month(config.follower_management['months_to_manage'])
        is True):

        followers = set(api.followers_ids(config.twitter_keys['screen_name']))
        following = set(api.friends_ids(config.twitter_keys['screen_name']))
        not_following_back = [item for item in followers if item not in following]
        following_back = [item for item in followers if item in following]

        if config.follower_management['aggressive_management'] is True:
            aggressive_management(api, config)
        else:
            passive_management(api, config, following, following_back)

        if config.follower_management['follow_back'] is True:
            follow_back(api, config, not_following_back)


@log_errors
def follow_back(api, config, not_following_list):
    """Follows back any users who you have not have reciprocated a connection with"""

    followed_users = 0

    for user in not_following_list[:config.follower_management['max_follows']]:
        api.create_friendship(user, True)
        followed_users += 1
        logging.info("Followed: %d", user)

    logging.info("Finished reciprocated follows. %d users followed.", followed_users)


@log_errors
def aggressive_management(api, config):
    """Unfollows any followers until rate limit is hit that aren't following back"""

    unfollowed_count = 0

    for page in tweepy.Cursor(api.friends, count=100).pages():
        user_ids = [user.id for user in page]
        friendships = api._lookup_friendships(user_ids)
        for user, friendship in zip(page, friendships):
            if unfollowed_count >= config.follower_management['max_unfollows']:
                return

            if not friendship.is_followed_by:
                api.destroy_friendship(user.id)
                unfollowed_count += 1
                logging.info("Unfollowed: %d", user.id)

    logging.info("Finished. %d unfollowed.", unfollowed_count)


def unfollow_inactive_followers(api, config, followers, inactivity_date, following_back):
    """Unfollows any followers after a configured inactivity period"""
    unfollowed_count = 0
    for follower in followers:
        if not config.follower_management['remove_followers'] and follower in following_back:
            continue

        if unfollowed_count >= config.follower_management['max_unfollows']:
            break

        last_tweet_date = api.user_timeline(follower, count=1)[0].created_at.date()

        if last_tweet_date >= inactivity_date:
            continue

        api.destroy_friendship(follower)
        unfollowed_count += 1
        logging.info("Unfollowed: %d", follower)
    return unfollowed_count


@log_errors
def passive_management(api, config, following, following_back):
    """Passive management unfollows any followers after a configured inactivity period"""

    inactivity_date = datetime.date.today(
    ) - datetime.timedelta(days=config.follower_management['inactivity_period'])
    unfollowed_count = 0
    chunk_size = 50

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        following_list = list(following)
        for i in range(0, len(following_list), chunk_size):
            chunk = following_list[i:i+chunk_size]
            future = executor.submit(
                unfollow_inactive_followers, api, config, chunk, inactivity_date, following_back)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            unfollowed_count += future.result()

    logging.info("Finished. %d unfollowed.", unfollowed_count)
