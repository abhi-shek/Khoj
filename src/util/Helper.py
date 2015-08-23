from ConfigParser import ConfigParser
import logging
from datetime import datetime, timedelta
from itertools import combinations
from itertools import chain

import re
import argparse


logger = logging.getLogger()


class Helper(object):

	TWEET_REGEX_PATT = "([http|https]*:\/\/.*[\r\n]*)|( +)|(\n)|(RT[\s]?@[\w]+:[\s]+)|(@(\w)+[\s]+)|([\s]+)"

	def __init__(self, prop_loc):
		self.app_prop_loc = prop_loc
		self.app_config = ConfigParser()

	def load_properties(self):
		logger.debug("loading properties")
		try:
			self.app_config.read(self.app_prop_loc)
		except Exception as e:
			logger.error("Exception :", e)
			return False

		return True

	@staticmethod
	def get_current_datetime():
		return datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

	@staticmethod
	def get_date(delta):
		current_date = datetime.now()
		if delta > 0:
			current_date = current_date + timedelta(days=delta)
		return current_date.strftime('%Y-%m-%d')

	@staticmethod
	def get_hashtags_combinations(ilist):
		# s = list(ilist)
		return chain.from_iterable(combinations(ilist, r) for r in range(len(ilist) + 1))

	@staticmethod
	def clean_tweet_text(in_tweet):
		pat = re.compile(Helper.TWEET_REGEX_PATT)
		o_string = re.sub(pat, " ",in_tweet).strip()
		return o_string

	@staticmethod
	def get_args(arg_list):
		parser = argparse.ArgumentParser(description='Command line options for the parser')
		parser.add_argument('-e', '--extract', action='store_true', help='Extracts tweets for hashtags', required=False)
		parser.add_argument('-c', '--clean', action='store_true',help='basic tweets cleaning', required=False)
		parser.add_argument('-ml', '--machinelearn', action='store_true',help='apply machine learning on cleaned data', required=False)
		args = parser.parse_args(arg_list)
		return args

	def __str__(self):
		return "Helper Utility"

