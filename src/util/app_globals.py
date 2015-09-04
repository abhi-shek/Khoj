APP_CONFIG = "../config/khoj_config.properties"
APP_LOG_CONFIG = "../config/app_log.conf"
APP_LOG_DIR = "../logs"
APP_DATA_DIR = "../data"
APP_TIDY_DATA = "../data/tidy_data"
APP_DATA_EXT = ".csv"
# days of hashtags data needs to be retrieved. Twitter indexes/stores previous 7 days tweet data
# Returns tweets created before the given date. Date should be formatted as YYYY-MM-DD.
# Keep in mind that the search index has a 7-day limit. In other words, no tweets will be found
# for a date older than one week.
APP_DAYS_COUNT = 1
APP_CSV_DELIM = "|"
APP_MAX_TWEET_COUNT=100 # maximum tweets needs to be retrieved for each hashtag, minimum 100
APP_MAX_TWEETS_PER_QUERY=100 # max value Twitter API permits