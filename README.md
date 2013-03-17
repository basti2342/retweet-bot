Python Retweet Bot
==================

This script retweets all Tweets containing your search term. To limit Twitter requests a savepoint file marks Tweets found before.

How to start:
-------------
* Uses "Searching Twitter with Python" by Derrick Petzold (http://derrickpetzold.com/p/twitter-python-search/) (licensed under CC BY-SA)
* Depends on http://tweepy.github.com/ (pip install tweepy)
* Put in your Twitter app credentials
* Define your hashtag
* $ python retweet.py
* Add this call to your crontab to retweet all new Tweets regularly
