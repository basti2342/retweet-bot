Python Retweet Bot
==================

![alt text](https://img.shields.io/badge/python-3.5-green.svg "Python3.5")

Forked from this project: https://github.com/basti2342/retweet-bot

- This script retweets all Tweets containing your search term. 
- Optionally, you can restrict retweets to people you follow
- Optionally, you can automatically follow users that use your search term
- A savepoint file is created each time the script is run so it can pick up where it left off the previous time it was run.
- Twitter API v1.1 ready. 

Setup:
-------------
- copy `sample-config` and rename to `config`
- fill out the config file for your project (more info in the file)

#### If running locally...
1. Install python 3. Maybe using virtualenv.
2. ```pip install -r requirements.txt```
3. ```python retweet.py```

#### If using Docker...
1. [Get Docker](https://www.docker.com/)
2. `docker-compose up`
3. `docker run -it bot`


