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
 logger.debug("connecting twitter with using %s ",access_details) 
 try:
  api = twitter.Api(
          consumer_key=access_details['consumer_key'],
          consumer_secret=access_details['consumer_secret'],
          access_token_key=access_details['access_token_key'],
          access_token_secret=access_details['access_token_secret']
      )
 # time the whole operation
  cpu_start_time,operation_start_time = time.clock(), time.time() 

 # modify this to get all tweets pertaining to specific hashtags

 #search = api.GetSearch(term='#india,#modi', lang='en', result_type='recent', count=10, max_id='')

 # this one uses geolocation tweets (india only)
 # 
  search = api.GetSearch(term=access_details['hashtags'], geocode='20.593684020,78.962880078,1500km',lang='en', result_type='recent', count=10, max_id='')
 #file_name = "_".join(["tweets",datetime.now().strftime('%Y_%m_%d_%H_%M_%S')])

  file_name = "_".join(["tweets",Helper.Helper.get_current_datetime()])
  file_name = app_globals.APP_DATA_DIR+"/"+file_name+app_globals.APP_DATA_EXT

  with open(file_name,"w") as ofile:
   ofile.write("id|tweet\n")
   id = 1
   for t in search:
    line = "|".join([str(id),t.text.encode('utf-8')])
    ofile.write(line)
    ofile.write("\n")
    id = id + 1

  # (CPU + Operation) time taken in seconds (getting + writing data to file)

  logger.debug("(seconds) CPU time [%s], Operation time [%s]", (time.clock() - cpu_start_time), (time.time() - operation_start_time))

 except Exception as te:
  logger.error(te)
  

def connect_facebook(credentials):
 logger.debug("shooo shooo... not implemented!!")

