import logging
import time
import csv

# import twitter
from util import Helper, app_globals
import tweepy
import jsonpickle

from sys import exit

# from tweepy import Stream
# from tweepy import OAuthHandler

# import tweets_listener

logger = logging.getLogger()

tweet_stats = []


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
		# api = twitter.Api(
		# 	consumer_key=access_details['consumer_key'],
		# 	consumer_secret=access_details['consumer_secret'],
		# 	access_token_key=access_details['access_token_key'],
		# 	access_token_secret=access_details['access_token_secret'],
		#  debugHTTP=True
		# )

		auth = tweepy.AppAuthHandler(consumer_key=access_details['consumer_key'],
		                             consumer_secret=access_details['consumer_secret'])
		api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
		if not api:
			logger.debug("Can't Authenticate")
			exit(-1)
		else:
			logger.debug("Authenticated..proceeding further")

		# we need to get all the combinations of the hastags
		# for each combination we need to query

		hash_comb = list(Helper.Helper.get_hashtags_combinations(access_details['hashtags'].split(",")))

		file_name = "_".join(["tweets", Helper.Helper.get_current_datetime()])
		file_name = app_globals.APP_DATA_DIR + "/" + file_name + app_globals.APP_DATA_EXT
		#csv_header = ["id","tweet_id","hashtags","retweet_count","retweeted","truncated","tweet_text"]
		csv_header = ["tweet_id", "created_at", "user_id", "user_name", "user_handle",
		              "hashtags", "retweet_count", "retweeted", "tweet_text", "location"]
		# write the header to the file
		with open(file_name, "ab") as ofile:
			w = csv.writer(ofile, delimiter=app_globals.APP_CSV_DELIM, lineterminator='\n')
			w.writerow(csv_header)

		global tweet_stats
		# create as many empty dictionaries as hashtags combinations
		# we will store statistics for each hashtag, internal purpose

		tweet_stats = [{'hashtag': '', 'total_tweet_count': 0} for i in range(len(hash_comb))]
		get_hashtags_data(api, hash_comb, file_name)
		logger.debug("Tweet stats -> %s ", str(tweet_stats))

	except Exception as e:
		logger.error(e, exc_info=True)


def get_hashtags_data(api, hash_tags, ofile):
	global tweet_stats
	logger.debug("we need to retireve [%s] days of hashtags data ", app_globals.APP_DAYS_COUNT)
	for days_count in range(1, app_globals.APP_DAYS_COUNT + 1):
		#search_before_date = Helper.Helper.get_date(days_count)
		startSince = Helper.Helper.get_start_end_date(days_count)
		endUntil = Helper.Helper.get_start_end_date(days_count - 1)
		logger.debug("Search start date [%s], end date [%s] ", startSince, endUntil)
		# iterate over each hashtags combinations
		for i, val in enumerate(hash_tags):
			if (0 == len(val)):
				continue
			else:
				search_term = ",".join(map(str, val))
				tweet_stats[i]['hashtag'] = search_term

				# time the operation of each individual/paired hashtags search
				cpu_start_time, operation_start_time = time.clock(), time.time()
				#search_twitter(api, search_term, ofile, i, search_before_date)
				tweet_count = search_twitter(api, search_term, ofile, i, startSince, endUntil)
				tweet_stats[i]['total_tweet_count'] += tweet_count
			# (CPU + Operation) time taken in seconds (getting + writing data to file)
			# includes wait time as well
			logger.debug("Hashtag [%s] in (seconds) CPU time [%s], Operation time [%s]",
			             val, (time.clock() - cpu_start_time), (time.time() - operation_start_time))


def search_twitter(api, hashtag, file_name, index, start_date, end_date):
	maxTweets = app_globals.APP_MAX_TWEET_COUNT  # Some arbitrary large number
	tweetsPerQry = app_globals.APP_MAX_TWEETS_PER_QUERY

	# If results from a specific ID onwards are reqd, set since_id to that ID.
	# else default to no lower limit, go as far back as API allows
	sinceId = None

	# If results only below a specific ID are, set last_id to that ID.
	# else default to no upper limit, start from the most recent tweet matching the search query.
	last_id = -1L

	tweet_count = 0
	jsonpickle.set_encoder_options('simplejson', indent=4, sort_keys=True)
	logger.debug("Downloading max {0} tweets".format(maxTweets))
	with open(file_name, 'ab') as f:
		w = csv.writer(f, delimiter=app_globals.APP_CSV_DELIM, lineterminator='\n')
		while tweet_count < maxTweets:
			try:
				if (last_id <= 0):
					if (not sinceId):
						new_tweets = api.search(q=hashtag, count=tweetsPerQry, result_type='mixed', since=start_date,
						                        until=end_date)
					else:
						new_tweets = api.search(q=hashtag, count=tweetsPerQry,
						                        since_id=sinceId, result_type='mixed', since=start_date, until=end_date)
				else:
					if (not sinceId):
						new_tweets = api.search(q=hashtag, count=tweetsPerQry,
						                        max_id=str(last_id - 1), result_type='mixed', since=start_date, until=end_date)
					else:
						new_tweets = api.search(q=hashtag, count=tweetsPerQry,
						                        max_id=str(last_id - 1),
						                        since_id=sinceId, result_type='mixed', since=start_date, until=end_date)
				if not new_tweets:
					logger.debug("No more tweets found")
					break
				for i, tweet in enumerate(new_tweets):
					# get all hashtags in the tweet
					hash_tags = [hash['text'].encode('utf-8') for hash in tweet.entities.get('hashtags')]
					# row to be appended
					line = [tweet.id_str, tweet.created_at, tweet.user.id_str, str(tweet.user.name.encode('utf-8')),
					        str(tweet.user.screen_name.encode('utf-8')), ",".join(hash_tags), str(tweet.retweet_count)]
					# dic to store all kinds of tweet texts
					tweets_text = {}
					tweets_list = []
					# we need to retrieve all relevant tweet texts for analysing
					if hasattr(tweet, 'quoted_status'):
						tweets_text['quoted_status'] = tweet.quoted_status['text'].encode('utf-8')
						tweets_list.append(tweet.quoted_status['text'].encode('utf-8'))
					else:
						tweets_text['quoted_status'] = ''

					if hasattr(tweet, 'retweeted_status'):
						line.append('True')
						tweet_text = tweet.retweeted_status.text.encode('utf-8')
						tweets_list.append(tweet.retweeted_status.text.encode('utf-8'))
						tweets_text['retweeted_status'] = tweet_text
						tweets_text['text'] = tweet.text.encode('utf-8')
					else:
						line.append('False')
						tweet_text =  tweet.text.encode('utf-8')
						tweets_list.append(tweet.text.encode('utf-8'))
						tweets_text['retweeted_status'] = ''
						tweets_text['text'] = tweet_text

					#logger.debug(jsonpickle.encode(tweets_text, unpicklable=False).encode('utf-8') + '\n')

					# do little bit cleaning of original text here itself
					# this is done so to check any issues in cleaning here itself
					# any special cleaning then will be added i.e. continuous cleaning
					tweet_text = ' '.join(tweets_list)
					#logger.debug("original text {%s} ", tweet_text)
					tweet_text = Helper.Helper.clean_tweet_text(tweet_text)
					#logger.debug("cleaned text {%s} ", tweet_text)
					line.append(tweet_text)

					# check for tweet location and fallback for each option
					if tweet.place:
						line.append('tplace,' + tweet.place.full_name.encode('utf-8'))
					elif tweet.user.location:
						line.append('ulocation,' + Helper.Helper.remove_punctuations(tweet.user.location.encode('utf-8')))
					elif tweet.user.time_zone:
						line.append('utz,' + tweet.user.time_zone.encode('utf-8'))
					else:
						line.append('NaN')
					w.writerow(line)
					line[:] = []

					# log all text retrieved
					#print (jsonpickle.encode(tweet._json, unpicklable=False) + '\n')

				tweet_count += len(new_tweets)
				logger.debug("Downloaded {0} tweets".format(tweet_count))
				last_id = new_tweets[-1].id
			except tweepy.TweepError as e:
				logger.error("Error : " + str(e))
				break
	return tweet_count


# def search_twitter(api, hashtag, file_name, index, search_before_date):
# 	global tweet_stats, tweet_id
# 	round_count, search_request_count, = 0, 0
# 	while round_count < app_globals.APP_HASHTAGS_REQ_COUNT:
# 		prev_tweet_count = tweet_stats[index]['total_tweet_count']
# 		while search_request_count < app_globals.APP_MAX_REQUEST:
# 			search_result = api.GetSearch(term=hashtag, lang='en', until=search_before_date,
# 			                              result_type='recent', count=100, max_id='',include_entities = True)
# 			search_request_count += 1
# 			tweet_count = 0
# 			logger.debug("tweet json -> %s " ,search_result[0].AsJsonString())
# 			# append tweets to the file
# 			with open(file_name, "ab") as ofile:
# 				w = csv.writer(ofile,delimiter = app_globals.APP_CSV_DELIM,lineterminator='\n')
# 				for t in search_result:
# 					hash_tags = [hash.text.encode('utf-8') for hash in t.hashtags]
# 					line = [str(tweet_id + 1), str(t.id), ",".join(hash_tags),str(t.retweet_count), str(t.retweeted), str(t.truncated),
# 					                 t.text.encode('utf-8')]
# 					#line = "|".join([str(tweet_id + 1), str(t.id), ",".join(hash_tags), str(t.retweeted), str(t.truncated),
# 					#                 t.text.encode('utf-8'), "\n"])
# 					w.writerow(line)
# 					tweet_id, tweet_count = tweet_id + 1, tweet_count + 1
#
# 			logger.debug("Hashtag [%s], Search Request Count [%s], Tweets retrieved [%s] ", hashtag,
# 			             search_request_count, tweet_count)
# 			tweet_stats[index]['total_tweet_count'] += tweet_count
#
# 		round_count += 1
# 		logger.debug("Hashtag [%s], Round [%s], Total Search Request Count [%s], Tweets retrieved [%s] ",
# 		             hashtag, round_count, search_request_count, tweet_stats[index]['total_tweet_count'] - prev_tweet_count)
# 		search_request_count = 0
#
# 		# till here we may have executed max search request supported by twitter API i.e. 450
# 		# regardless, we need to sleep for 15 minutes or more to issue next round of search
# 		logger.debug("Current time [%s], Sleeping for [%d] minutes ", Helper.Helper.get_current_datetime(),
# 		             app_globals.APP_SEARCH_INTERVAL_TIME)
# 		time.sleep(app_globals.APP_SEARCH_INTERVAL_TIME * 60)
# 		logger.debug("Woke up at [%s] ", Helper.Helper.get_current_datetime())


def connect_facebook(credentials):
	logger.debug("shooo shooo... not implemented!!")

