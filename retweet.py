# -*- coding: utf-8 -*-

import os, configparser, tweepy, inspect, hashlib, time

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# read config
config = configparser.SafeConfigParser()
config.read(os.path.join(path, "config"))

# your hashtag or search query and tweet language (empty = all languages)
hashtag = config.get("settings", "search_query")

# if you would like to automatically follow once you retweet
auto_follow = config.getboolean("settings", "auto_follow")

# if you would only like to retweet people you follow (overrides auto-follow)
only_retweet_friends = config.getboolean("settings", "only_retweet_friends")

# Number retweets per time
num = int(config.get("settings","max_num_retweets"))

# set pagerduty API key
using_pd = False
try:
    pypd.api_key = config.get("pagerduty", "api_key")
    integration_key = config.get("pagerduty", "integration_key")
    using_pd = True
except:
    pass

# blacklisted users and words
userBlacklist = []
wordBlacklist = ["RT", u"♺"]
friends = []

# build savepoint path + file
# os.chdir('/tmp')
hashedHashtag = hashlib.md5(hashtag.encode('ascii')).hexdigest()
last_id_filename = "last_id_hashtag_%s" % hashedHashtag
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join("/tmp", last_id_filename)

# create bot
auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
api = tweepy.API(auth)

def refresh_friends():
    try:
        friends = api.friends_ids(config.get("settings", "retweet_account"))
        print("Friends refreshed")
    except Exception as e:
        print("friends refresh failed")
        print(e)

refresh_friends()

def retweet_bot():

    # retrieve last savepoint if available
    try:
        with open(last_id_file, "r") as file:
            savepoint = file.read()
    except:
        savepoint = ""
        print("No savepoint found. Bot is now searching for results")

    # search query
    timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint).items(num)

    # put everything into a list to be able to sort/filter
    timeline = []

    try:
        for status in timelineIterator:
            timeline.append(status)
    except TweepError as e:
        print('Tweepy Error caught on timelineIterator: ' + str(e))
        if using_pd:
            pypd.EventV2.create(data={
                'routing_key': integration_key,
                'event_action': 'trigger',
                'payload': {
                    'summary': 'Tweepy Error caught on timelineIterator: ' + str(e),
                    'severity': 'error',
                    'source': 'Python Retweet Bot',
                }
            })
        time.sleep(20)

    try:
        last_tweet_id = timeline[0].id
    except IndexError:
        last_tweet_id = savepoint

    # filter @replies/blacklisted words & users out and reverse timeline
    #timeline = filter(lambda status: status.text[0] = "@", timeline)   - uncomment to remove all tweets with an @mention
    timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)
    timeline = filter(lambda status: status.author.screen_name not in userBlacklist, timeline)

    if only_retweet_friends:
        timeline = filter(lambda status: status.author.id in friends, timeline)

    timeline = list(timeline)
    timeline.reverse()

    tw_counter = 0
    err_counter = 0

    # iterate the timeline and retweet
    for status in timeline:
        try:
            print("(%(date)s) %(name)s: %(message)s\n" % \
                  {"date": status.created_at,
                   "name": status.author.screen_name.encode('utf-8'),
                   "message": status.text.encode('utf-8')})
            api.retweet(status.id)

            if auto_follow and status.author.id not in friends:

                try:
                    print("Auto-following: %(name)s" % \
                      {"name": status.author.screen_name.encode('utf-8')})
                    api.create_friendship(status.author.id)
                except tweepy.error.TweepError as e:
                    print("Unable to follow " + status.author.screen_name.encode('utf-8'))
                    print(e)
                    err_counter += 1

                friends.append(status.author.id)

            tw_counter += 1
        except tweepy.error.TweepError as e:
            # just in case tweet got deleted in the meantime or already retweeted
            err_counter += 1
            print(e)
            continue

    print("Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter))

    # write last retweeted tweet id to file
    with open(last_id_file, "w") as file:
        file.write(str(last_tweet_id))



def handler(event, context):
    retweet_bot()
