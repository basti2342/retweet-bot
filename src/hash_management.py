# Retweet Bot hashes management responsible for creating and maintaining search hashes

import hashlib
import logging
import os


def create_hashes_folder():
    """Checks if the hashes directory exists, if not create it"""

    if not os.path.exists('hashes'):
        os.makedirs('hashes')


def get_hash_file_id(hashtag):
    """Gets the file id of the passed hashtag"""

    hashed_hashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
    last_id_filename = "last_id_hashtag_%s" % hashed_hashtag
    last_id_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'hashes', last_id_filename))

    return last_id_file


def get_hash_savepoint(hashtag):
    """Gets the last retweet id of the passed hashtag if it exists"""

    try:
        with open(get_hash_file_id(hashtag), "r") as file:
            savepoint = file.read()
    except IOError:
        savepoint = ""
        logging.warning("No savepoint found. Bot is now searching for results")

    return savepoint