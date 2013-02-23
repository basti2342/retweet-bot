#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
import twitter

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
hashtag = "#yourhashtag"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
bot = tweepy.API(auth)

last_id_filename = "last_id_hashtag_" + hashtag

try:
	file = open(last_id_filename, "r")
	savepoint = file.read()
	file.close()
except IOError:
	savepoint = ""

print asctime(), "Doing a search ...",
twit = twitter.Twitter(True)

# search query
timeline = twit.search(hashtag, since_id=savepoint, max_results=999)
print len(timeline),"items found."

# filter @replies out and reverse timeline
timeline = filter(lambda status: status["text"][0] != "@", timeline)
timeline.reverse()

for status in timeline:
	print "%(screenname)s: %(statusmessage)s\n\n" \
		% {"screenname" : status["from_user"], "statusmessage" : status["text"]}
	try:
		bot.retweet(status["id"])
	except tweepy.error.TweepError:
		continue

# write last retweeted tweet id to file
if len(timeline) != 0:
	file = open(last_id_filename, "w")
	file.write(str(timeline[-1]["id"]))
	file.close()

