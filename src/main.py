"""Entry point to the Twitter bot"""

import logging
import asyncio
import retweet_core
import hash_management
import follower_management
import config


async def main():
    """Entry point method for bots async tasks"""
    loaded_config = config.Config()
    logging.basicConfig(level = logging.getLevelName(loaded_config.general['log_level']))
    logging.info("Bot started")

    api = retweet_core.api_login(loaded_config.twitter_keys)

    hash_management.create_hashes_folder()

    retweet_task = asyncio.create_task(retweet_core.retweet(api, loaded_config.query_objects))
    follower_task = asyncio.create_task(follower_management.manage_followers(api, loaded_config))
    await asyncio.gather(retweet_task, follower_task)

if __name__ == '__main__':
    asyncio.run(main())
