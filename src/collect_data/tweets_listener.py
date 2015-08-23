__author__ = 'himanshurawat'

from tweepy.streaming import StreamListener

import logging

from tweepy.utils import import_simplejson

from util import Helper, app_globals
import time

logger = logging.getLogger()
json = import_simplejson()

class tistener(StreamListener):

	def on_connect(self):
		logger.debug("we have connected to twitter streaming api")
		return True

	def on_data(self,data):

		#to_log = json.dumps(data,sort_keys=True, indent=4,separators=(',',': '))
		#print ("data -> ", to_log)
		tweet_data = json.loads(data)
		logger.debug("Tweets are -> %s ", tweet_data['text'].encode('utf-8'))
		return True

	def on_limit(self,track):
		logger.debug("we have reached limit ", track)
		return False

	def on_error(self,status):
		logger.debug("on_error -> ", status)
		if status == 420:
			return False

	def on_timeout(self):
		logger.debug("we got timeout ")
		return True

	def on_warning(self,notice):
		logger.debug("we got warning " , notice)
		return True
