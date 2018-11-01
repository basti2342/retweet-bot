FROM python:3.5
RUN mkdir /myapp
WORKDIR /myapp
ADD . /myapp
RUN pip install -r /myapp/requirements.txt
CMD ["python", "-u", "/myapp/retweet.py"]
