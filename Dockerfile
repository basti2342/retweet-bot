FROM python:3

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD /bin/bash

# COPY . .

# CMD [ "python", "./retweet.py" ]