from ConfigParser import ConfigParser
import logging
from datetime import datetime
from itertools import combinations
from itertools import chain

logger = logging.getLogger()

class Helper(object):
 
 def __init__(self,prop_loc):
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
 def get_hashtags_combinations(ilist):
  #s = list(ilist)
  return chain.from_iterable(combinations(ilist, r) for r in range(len(ilist)+1))

 def __str__(self):
  return "Helper Utility"

