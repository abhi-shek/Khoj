from ConfigParser import ConfigParser
import logging
from datetime import datetime, timedelta
from itertools import combinations
from itertools import chain

import re
import argparse
import os.path
import glob
from util import app_globals

logger = logging.getLogger()


class Helper(object):
	# TWEET_REGEX_PATT = '([http|https]*:\/\/.*[\r\n]*)|' \
	#                    '( +)|' \
	#                    '( \n)|' \
	#                    '(RT[\s]?@[\w]+:[\s]+)|' \
	#                    '(@(\w)+[\s]*)|' \
	#                    '([\s]+)|' \
	#                    '(RT)*[\s]+'

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
	def get_start_end_date(delta):
		current_date = datetime.now()
		current_date = current_date - timedelta(days=delta)
		return current_date.strftime('%Y-%m-%d')

	@staticmethod
	def get_hashtags_combinations(ilist):
		# s = list(ilist)
		return chain.from_iterable(combinations(ilist, r) for r in range(len(ilist) + 1))

	@staticmethod
	def clean_tweet_text(in_tweet):

		# Convert to lower case
		o_string = in_tweet.lower()

		#Convert www.* or https?://* to URL
		o_string = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', ' ', o_string)

		#remove @username
		o_string = re.sub('@[^\s]+', ' ', o_string)

		#Replace #word with word
		o_string = re.sub(r'#([^\s]+)', r'\1', o_string)

		#Remove RT
		o_string = re.sub('^rt[\s]+', ' ', o_string)

		o_string = o_string.replace('^M', '')

		# few smart people use @ instead at
		o_string = o_string.replace('@', 'at')

		# remove html tags
		o_string = Helper.remove_html_tags(o_string)

		# remove all punctuations
		o_string = Helper.remove_punctuations(o_string)

		#Remove additional white spaces
		o_string = re.sub('[\s]+', ' ', o_string)

		return o_string.strip(' \t\n\r')

	@staticmethod
	def remove_html_tags(text):
		# replace special strings
		special = {
			'&nbsp;': '', '&amp;': '', '&quot;': '',
			'&lt;': '', '&gt;': ''
		}
		for (k, v) in special.items():
			text = text.replace(k, v)
		return text

	@staticmethod
	def remove_punctuations(text):
		o_string = re.sub(r"['|:_,!\-\"\\\/}{?\.;]", ' ', text).strip()
		return o_string

	@staticmethod
	def get_args(arg_list):
		parser = argparse.ArgumentParser(description='Command line options for the parser')
		parser.add_argument('-e', '--extract', action='store_true', help='Extracts tweets for hashtags', required=False)
		parser.add_argument('-c', '--clean', action='store_true', help='basic tweets cleaning', required=False)
		# parser.add_argument('-ml', '--machinelearn', action='store_true',help='apply machine learning', required=False)
		args = parser.parse_args(arg_list)
		return args

	@staticmethod
	def get_latest_file_dir():
		newest = max(glob.iglob(os.path.join(app_globals.APP_TIDY_DATA, '*.csv')), key=os.path.getctime)
		return newest

	def __str__(self):
		return "Helper Utility"

