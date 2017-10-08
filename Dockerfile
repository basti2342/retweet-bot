FROM python:3-jessie

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
      apt-get -y install \
      sudo \
      lsb-release

RUN export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s` \
  && echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - \
  && sudo apt-get update \
  && sudo apt-get install -y gcsfuse

COPY ["google-key.json", "start.sh", "retweet.py", "config", "/app/"]

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/google-key.json

WORKDIR /app
RUN mkdir store
ENTRYPOINT ["bash","./start.sh"]

CMD [ "python", "retweet.py" ]