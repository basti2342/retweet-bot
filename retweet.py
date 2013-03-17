#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
import twitter
import os

# provide your credentials and hashtag
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
hashtag = "#yourHashtag"

# build savepoint path + file
last_id_filename = "last_id_hashtag_%s" % hashtag.replace("#", "")
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(rt_bot_path, last_id_filename)

# create bot
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
bot = tweepy.API(auth)

# retrieve last savepoint if available
try:
	with open(last_id_file, "r") as file:
		savepoint = file.read()
except IOError:
	savepoint = ""
	print "No savepoint found. Trying to get as many results as possible."

# search query
twit = twitter.Twitter()
timeline = twit.search(hashtag, since_id=savepoint, max_results=999)

if len(timeline) == 0:
	print "No Tweets matched your search query."
	quit()

last_tweet_id = timeline[-1]["id"]

# filter @replies out and reverse timeline
timeline = filter(lambda status: status["text"][0] != "@", timeline)
timeline.reverse()

print "%d new Tweets found." % len(timeline)

counter = 0
# iterate the timeline and retweet
for status in timeline:
	try:
		print "(%(date)s) %(name)s: %(message)s\n" % \
			{ "date" : status["created_at"].encode('utf-8'),
			"name" : status["from_user"].encode('utf-8'),
			"message" : status["text"].encode('utf-8') }

		bot.retweet(status["id"])
		counter += 1
	except tweepy.error.TweepError:
		# just in case tweet got deleted in the meantime or already retweeted
		continue

print "Finished. %d Tweets retweeted." % counter

# write last retweeted tweet id to file
with open(last_id_file, "w") as file:
	file.write(str(last_tweet_id))

