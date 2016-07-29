Python Retweet Bot
==================

![alt text](https://img.shields.io/badge/python-3.5-green.svg "Python3.5")

This script retweets all Tweets containing your search term. To limit Twitter requests a savepoint file marks Tweets found before. It's Twitter API v1.1 ready.

Dependecies:
-------------
* Tweepy

```pip install tweepy```

* Or alternatively

```pip install -r requirements.txt```

How to start:
-------------

* Define your hashtag or search query in the config file
* Define the number of Retweets at a time (This avoids overloading -Limit is 180 RT/ 15 mins)
* Add your Twitter app credentials in the config file
* (Tune some other options if you like)
* $ python retweet.py
* Add this call to your crontab(unix)/task scheduler(windows) (or something similar) to retweet all new tweets regularly

Compatibility
-------------

Compatible with Python 3.x ,tested  on Python 3.5.
