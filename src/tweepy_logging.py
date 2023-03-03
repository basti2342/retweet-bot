"""Retweet Bot try/except logic decorator to gracefully handle rate limit errors"""

import logging
import tweepy


def log_errors(func):
    """Decorator method to perform error handling within the application"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except tweepy.RateLimitError as err:
            logging.error("Hit rate limit, breaking out of current process.")
            raise err
        except tweepy.TweepError as err:
            error_code = err.response.json()['errors'][0]['code']
            if error_code == 161:
                logging.error(
                    "Unable to follow more people at this time, breaking out of current process.")
                raise err
        except Exception as err:
            logging.exception(err)
    return wrapper
