from ConfigParser import ConfigParser
import logging

logger = logging.getLogger()

class Helper:
 
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
 
 def __str__(self):
  return "Helper Utility"

