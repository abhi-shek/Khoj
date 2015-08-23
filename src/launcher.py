#!/usr/bin/env python

import os.path

from util import Helper, app_globals
from collect_data import get_data,clean_data
import sys

def housekeeping():
	# validate config files, abort if missing
	# check app config file
	if not os.path.isfile(app_globals.APP_CONFIG):
		logger.critical("check app config file for existence..aborting the launch")
		exit()


def checkpoint():
	# check existence of log dir, create if missing
	# we can take backups of logs in future
	if not os.path.exists(app_globals.APP_LOG_DIR):
		os.makedirs(app_globals.APP_LOG_DIR)
	if not os.path.exists(app_globals.APP_DATA_DIR):
		os.makedirs(app_globals.APP_DATA_DIR)
	if not os.path.exists(app_globals.APP_TIDY_DATA):
		os.makedirs(app_globals.APP_TIDY_DATA)
	if not os.path.isfile(app_globals.APP_LOG_CONFIG):
		exit()


def launch():
	# read the application properties
	helper = Helper.Helper(app_globals.APP_CONFIG)
	if (helper.load_properties()):
		logger.debug("Application properties loaded successfulli")
	else:
		logger.critical("Failed loading the application properties...aborting the launch")

	# iterate sections and get data from there
	# currently supporting twitter but others...hell yes

	for sec in helper.app_config.sections():
		get_data.connect(sec, dict(helper.app_config.items(sec)))


if __name__ == '__main__':
	import logging
	import logging.config
	checkpoint()
	logging.config.fileConfig(app_globals.APP_LOG_CONFIG)
	logger = logging.getLogger(__name__)
	housekeeping()
	app_launch_options = Helper.Helper.get_args(sys.argv[1:])
	logger.info("Launching the khoj with options %s", ",".join(sys.argv[1:]))
	if app_launch_options.extract:
		logger.debug("Extracting data..")
		launch()
	if app_launch_options.clean:
		logger.debug("Cleaning the extracted data..")
		clean_data.tidy_data()
	if app_launch_options.machinelearn:
		logger.warning("Not implemented!!")

	logger.info("Launch done!!")

