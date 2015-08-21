APP_CONFIG = "../config/khoj_config.properties"
APP_LOG_CONFIG = "../config/app_log.conf"
APP_LOG_DIR = "../logs"
APP_DATA_DIR = "../data"
APP_DATA_EXT = ".csv"
APP_MAX_REQUEST = 10 #Twitter max request for OAuth applications, max is 450
APP_HASHTAGS_REQ_COUNT = 3 #for each hashtag, query these many times
APP_SEARCH_INTERVAL_TIME = 2 # time to wait before issuing Twitter API search request
# days of hashtags data needs to be retrieved. Twitter indexes/stores previous 7 days tweet data
# Returns tweets created before the given date. Date should be formatted as YYYY-MM-DD.
# Keep in mind that the search index has a 7-day limit. In other words, no tweets will be found
# for a date older than one week.
APP_DAYS_COUNT = 1
APP_CSV_DELIM = "|"