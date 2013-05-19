#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
import os

# provide your credentials
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

# your hashtag or search query and tweet language (empty = all languages)
hashtag = "#yourHashtag"
tweetLanguage = ""

# blacklisted users and words
userBlacklist = []
wordBlacklist = ["RT", u"♺"]

# build savepoint path + file
last_id_filename = "last_id_hashtag_%s" % hashtag.replace("#", "").split(" ")[0]
rt_bot_path = os.path.dirname(os.path.abspath(__file__))
last_id_file = os.path.join(rt_bot_path, last_id_filename)

# create bot
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# retrieve last savepoint if available
try:
	with open(last_id_file, "r") as file:
		savepoint = file.read()
except IOError:
	savepoint = ""
	print "No savepoint found. Trying to get as many results as possible."

# search query
timelineIterator = tweepy.Cursor(api.search, q=hashtag, since_id=savepoint, lang=tweetLanguage).items()

# put everything into a list to be able to sort/filter
timeline = []
for status in timelineIterator:
	timeline.append(status)

try:
    last_tweet_id = timeline[0].id
except IndexError:
    last_tweet_id = savepoint

# filter @replies/blacklisted words & users out and reverse timeline
timeline = filter(lambda status: status.text[0] != "@", timeline)
timeline = filter(lambda status: not any(word in status.text.split() for word in wordBlacklist), timeline)
timeline = filter(lambda status: status.from_user not in userBlacklist, timeline)
timeline.reverse()

tw_counter = 0
err_counter = 0

# iterate the timeline and retweet
for status in timeline:
	try:
		print "(%(date)s) %(name)s: %(message)s\n" % \
			{ "date" : status.created_at,
			"name" : status.from_user.encode('utf-8'),
			"message" : status.text.encode('utf-8') }

		api.retweet(status.id)
		last_tweet_id = status.id
		tw_counter += 1
	except tweepy.error.TweepError:
		# just in case tweet got deleted in the meantime or already retweeted
		err_counter += 1
		continue

print "Finished. %d Tweets retweeted, %d errors occured." % (tw_counter, err_counter)

# write last retweeted tweet id to file
with open(last_id_file, "w") as file:
	file.write(str(last_tweet_id))

