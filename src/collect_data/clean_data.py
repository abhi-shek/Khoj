#!/usr/bin/env python

import csv
import logging

from os import listdir
from util import Helper, app_globals


logger = logging.getLogger(__name__)
# once all the data has been collected we need
# to undergo a little clean up befoe we can process the tweets
# Below are removed from tweets and replaced with single white space
# 1. http or https links
# 2. mutliple white space
# 3. newline character
# 4. RT @name:
# 5. @name

def tidy_data():
	cleaned_file = "_".join(["tidy_data", Helper.Helper.get_current_datetime()])
	cleaned_file = app_globals.APP_TIDY_DATA + "/" + cleaned_file + app_globals.APP_DATA_EXT
	o_file = open(cleaned_file, "ab+")
	writer = csv.writer(o_file, delimiter="|", lineterminator="\n")

	for dfile in listdir(app_globals.APP_DATA_DIR):
		if dfile.endswith(app_globals.APP_DATA_EXT):
			rfile = app_globals.APP_DATA_DIR+"/"+dfile
			with open(rfile, "rbU") as ifile:
				logger.debug("reading file -> %s ", rfile)
				r = csv.reader(ifile, delimiter="|", lineterminator="\n")
				for i, line in enumerate(r):
					line[-2] = Helper.Helper.clean_tweet_text(line[-2])
					writer.writerow(line)
	o_file.close()

if __name__ == '__main__':
	#from src.util import Helper,app_globals
 	print "cleaning the tweet data"
 	tidy_data()
 	print "DONE!!"