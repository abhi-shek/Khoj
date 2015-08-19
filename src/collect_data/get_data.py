import twitter
import logging
import time
from util import Helper,app_globals

logger = logging.getLogger()

def connect(data_from,credentials):
 if (data_from == "twitter"):
  logger.debug("initiate section [%s]", data_from)
  connect_twitter(credentials)
 elif (data_from == "facebook"):
  connect_facebook(credentials)
 else:
  logger.debug("[%s] is not supported", data_from)

def connect_twitter(access_details):
 try:
  api = twitter.Api(
          consumer_key=access_details['consumer_key'],
          consumer_secret=access_details['consumer_secret'],
          access_token_key=access_details['access_token_key'],
          access_token_secret=access_details['access_token_secret']
      )
 # time the whole operation
  cpu_start_time,operation_start_time = time.clock(), time.time() 

 # we need to get all the combinations of the hastags
 # for each combination we need to query
  hash_comb = list(Helper.Helper.get_hashtags_combinations(access_details['hashtags'].split(",")))
  tweet_id,tweet_count = 1,1
  file_name = "_".join(["tweets",Helper.Helper.get_current_datetime()])
  file_name = app_globals.APP_DATA_DIR+"/"+file_name+app_globals.APP_DATA_EXT
  for i,val in enumerate(hash_comb):
   if (0 == len(val)): continue
   else:
    hashtag_list = ",".join(map(str,val)) 
    search = api.GetSearch(term=hashtag_list , lang='en', result_type='recent', count=10, max_id='')
 # this one uses geolocation tweets (india only)
 # 
 #search = api.GetSearch(term=access_details['hashtags'], geocode='20.593684020,78.962880078,1km',lang='en', result_type='recent', count=10, max_id='')
    
    with open(file_name,"a") as ofile:
     for t in search:
      line = "|".join([str(tweet_id),t.text.encode('utf-8'),"\n"])
      ofile.write(line)
      tweet_id,tweet_count = tweet_id + 1,tweet_count + 1
   logger.debug("Tweets count containing hashtag -> [%s][%d]", hashtag_list,tweet_count)
   tweet_count = 0
  # (CPU + Operation) time taken in seconds (getting + writing data to file)

  logger.debug("(seconds) CPU time [%s], Operation time [%s]", (time.clock() - cpu_start_time), (time.time() - operation_start_time))

 except Exception as te:
  logger.error(te, exc_info=True)
  #logger.exception("Traceback : ", te)
  

def connect_facebook(credentials):
 logger.debug("shooo shooo... not implemented!!")

