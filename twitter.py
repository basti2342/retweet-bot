#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import urllib
import urlparse

# "Searching Twitter with Python" by Derrick Petzold
# http://derrickpetzold.com/p/twitter-python-search/
# v1.1 (since_id added) licensed under CC BY-SA
class Twitter(object):

	search_url = 'http://search.twitter.com/search.json'

	def __init__(self, verbose=False):
		self.verbose = verbose
		super(Twitter, self).__init__()

	def search(self, query, until=None, rpp=100, since_id="", max_results=None):

		results = []
		params = {
			'q': query,
			'rpp': rpp,
			'since_id' : since_id,
		}
		if until:
			params['until'] = until.strftime('%Y-%m-%d')

		if self.verbose:
			print(params)

		url = '%s?%s' % (self.search_url, urllib.urlencode(params))
		response = json.loads(urllib.urlopen(url).read())
		results.extend(response['results'])

		if len(results) >= max_results:
			return results

		while 'next_page' in response:
			url = self.search_url + response['next_page']
			response = json.loads(urllib.urlopen(url).read())

			if self.verbose:
				print('%s: %s' % (url, len(response['results'])))

			results.extend(response['results'])
			if len(results) >= max_results:
				break
		return results

	def search_last_day(self, *args, **kwargs):
		kwargs['until'] = datetime.datetime.now() - datetime.timedelta(days=1)

		return self.search(*args, **kwargs)
