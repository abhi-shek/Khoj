import logging
import time
import csv

import twitter
from util import Helper, app_globals


# from tweepy import Stream
# from tweepy import OAuthHandler

# import tweets_listener

logger = logging.getLogger()

tweet_stats = []
tweet_id = 0


def connect(data_from, credentials):
	if data_from == "twitter":
		logger.debug("initiate section [%s]", data_from)
		connect_twitter(credentials)
	elif data_from == "facebook":
		connect_facebook(credentials)
	else:
		logger.debug("[%s] is not supported", data_from)


def connect_twitter(access_details):
	# auth = OAuthHandler(access_details['consumer_key'], access_details['consumer_secret'])
	# auth.set_access_token(access_details['access_token_key'], access_details['access_token_secret'])
	#
	# # time the whole operation
	# cpu_start_time, operation_start_time = time.clock(), time.time()
	#
	# tweet_stream = Stream(auth = auth,listener = tweets_listener.tistener())
	# print("we are here")
	# try:
	# tweet_stream.filter(track=['#modi'])
	# except Exception as e:
	# 	logger.error(e, exc_info=True)
	#
	# logger.debug("Total (seconds) CPU time [%s], Operation time [%s]", (time.clock() - cpu_start_time), (time.time() - operation_start_time))

	try:
		api = twitter.Api(
			consumer_key=access_details['consumer_key'],
			consumer_secret=access_details['consumer_secret'],
			access_token_key=access_details['access_token_key'],
			access_token_secret=access_details['access_token_secret']
		)

		# we need to get all the combinations of the hastags
		# for each combination we need to query

		hash_comb = list(Helper.Helper.get_hashtags_combinations(access_details['hashtags'].split(",")))

		file_name = "_".join(["tweets", Helper.Helper.get_current_datetime()])
		file_name = app_globals.APP_DATA_DIR + "/" + file_name + app_globals.APP_DATA_EXT
		csv_header = ["id","tweet_id","hashtags","retweet","truncated","tweet_text"]
		# write the header to the file
		with open(file_name, "ab") as ofile:
			w = csv.writer(ofile, delimiter = app_globals.APP_CSV_DELIM, lineterminator='\n')
			w.writerow(csv_header)

		global tweet_stats
		# create as many empty dictionaries as hashtags combinations
		# we will store statistics for each hashtag, internal purpose

		tweet_stats = [{'hashtag': '', 'total_tweet_count': 0} for i in range(len(hash_comb))]

		get_hashtags_data(api, hash_comb, file_name)

		# iterate over each hashtags combinations
		# for i, val in enumerate(hash_comb):
		# 	if (0 == len(val)):
		# 		continue
		# 	else:
		# 		search_term = ",".join(map(str, val))
		# 		tweet_stats[i]['hashtag'] = search_term
		#
		# 		# time the operation of each individual/paired hashtags search
		# 		cpu_start_time, operation_start_time = time.clock(), time.time()
		# 		search_twitter(api,search_term, file_name, i)

		# 	hashtag_list = ",".join(map(str, val))
		#
		# 	search = api.GetSearch(term=hashtag_list, lang='en', result_type='mixed', count=100, max_id='')
		# 	search_request_count += 1
		#
		# 	# TODO : not working, need to research more
		# 	# this one uses geolocation tweets (india only)
		# 	# search = api.GetSearch(term=access_details['hashtags'], geocode='20.593684020,78.962880078,1km',
		# 	#                           lang='en', result_type='recent', count=10, max_id='')
		#
		# 	with open(file_name, "a") as ofile:
		# 		for t in search:
		# 			line = "|".join([str(tweet_id + 1), t.text.encode('utf-8'), "\n"])
		# 			ofile.write(line)
		# 			tweet_id, tweet_count = tweet_id + 1, tweet_count + 1
		#
		# logger.debug("Tweets count containing hashtag -> [%s][%d]", hashtag_list, tweet_count)
		# tweet_count = 0

		# (CPU + Operation) time taken in seconds (getting + writing data to file)
		# 	logger.debug("Hashtag [%s] in (seconds) CPU time [%s], Operation time [%s]",
		#           val, (time.clock() - cpu_start_time), (time.time() - operation_start_time))

		logger.debug("Tweet stats -> %s ", str(tweet_stats))
	except Exception as te:
		logger.error(te, exc_info=True)


def get_hashtags_data(api, hash_tags, ofile):
	logger.debug("we need to retireve [%s] days of hashtags data ", app_globals.APP_DAYS_COUNT)
	for days_count in range(1, app_globals.APP_DAYS_COUNT + 1):
		search_before_date = Helper.Helper.get_date(days_count)
		logger.debug("Search before date [%s] ", search_before_date)
		# iterate over each hashtags combinations
		for i, val in enumerate(hash_tags):
			if (0 == len(val)):
				continue
			else:
				search_term = ",".join(map(str, val))
				tweet_stats[i]['hashtag'] = search_term

				# time the operation of each individual/paired hashtags search
				cpu_start_time, operation_start_time = time.clock(), time.time()
				search_twitter(api, search_term, ofile, i, search_before_date)

			# (CPU + Operation) time taken in seconds (getting + writing data to file)
			# includes wait time as well
			logger.debug("Hashtag [%s] in (seconds) CPU time [%s], Operation time [%s]",
			             val, (time.clock() - cpu_start_time), (time.time() - operation_start_time))


def search_twitter(api, hashtag, file_name, index, search_before_date):
	global tweet_stats, tweet_id
	round_count, search_request_count, = 0, 0
	while round_count < app_globals.APP_HASHTAGS_REQ_COUNT:
		prev_tweet_count = tweet_stats[index]['total_tweet_count']
		while search_request_count < app_globals.APP_MAX_REQUEST:
			search_result = api.GetSearch(term=hashtag, lang='en', until=search_before_date,
			                              result_type='recent', count=100, max_id='')
			search_request_count += 1
			tweet_count = 0
			# append tweets to the file
			with open(file_name, "ab") as ofile:
				w = csv.writer(ofile,delimiter = app_globals.APP_CSV_DELIM,lineterminator='\n')
				for t in search_result:
					hash_tags = [hash.text.encode('utf-8') for hash in t.hashtags]
					line = [str(tweet_id + 1), str(t.id), ",".join(hash_tags), str(t.retweeted), str(t.truncated),
					                 t.text.encode('utf-8')]
					#line = "|".join([str(tweet_id + 1), str(t.id), ",".join(hash_tags), str(t.retweeted), str(t.truncated),
					#                 t.text.encode('utf-8'), "\n"])
					w.writerow(line)
					tweet_id, tweet_count = tweet_id + 1, tweet_count + 1

			logger.debug("Hashtag [%s], Search Request Count [%s], Tweets retrieved [%s] ", hashtag,
			             search_request_count, tweet_count)
			tweet_stats[index]['total_tweet_count'] += tweet_count

		round_count += 1
		logger.debug("Hashtag [%s], Round [%s], Total Search Request Count [%s], Tweets retrieved [%s] ",
		             hashtag, round_count, search_request_count, tweet_stats[index]['total_tweet_count'] - prev_tweet_count)
		search_request_count = 0

		# till here we may have executed max search request supported by twitter API i.e. 450
		# regardless, we need to sleep for 15 minutes or more to issue next round of search
		logger.debug("Current time [%s], Sleeping for [%d] minutes ", Helper.Helper.get_current_datetime(),
		             app_globals.APP_SEARCH_INTERVAL_TIME)
		time.sleep(app_globals.APP_SEARCH_INTERVAL_TIME * 60)
		logger.debug("Woke up at [%s] ", Helper.Helper.get_current_datetime())


def connect_facebook(credentials):
	logger.debug("shooo shooo... not implemented!!")

