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

### If running locally...
1. Install python 3. Maybe using virtualenv.
2. ```pip install -r requirements.txt```
3. ```python retweet.py```

### If using Docker...
#### Setting up Google Cloud Storage
Docker containers are meant to be stateless, so any files saved will be lost when the container stops running. To store the savepoint file, the docker container uses [gcsfuse](https://github.com/GoogleCloudPlatform/gcsfuse) to mount a Google Cloud Storage bucket and saves the file there. GCS was chosen because it has an [always free tier](https://cloud.google.com/free/docs/always-free-usage-limits).
1. Create a Google Cloud account. Under storage, create a regional bucket (free).
2. In `start.sh`, put your bucket name
3. [Create and download a service account JSON google key](https://cloud.google.com/storage/docs/authentication#generating-a-private-key). This gives the bot access to your bucket. (This may not be required if you're running docker on a Google Compute Engine instance.)
4. Put the key in the same folder as `retweet.py` and rename it to `google-key.json`

#### Run docker container
1. [Get Docker](https://www.docker.com/)
2. `docker-compose up`
3. `docker-compose run bot`


