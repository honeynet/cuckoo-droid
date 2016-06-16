# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.
# Originally contributed by Check Point Software Technologies, Ltd.

import logging
import sys
import time
import os
from lib.api import adb
from threading import Thread
from lib.api.droidbot.dtypes import App, Device
from lib.api.droidbot.event import AppEventManager
from lib.common.abstracts import Auxiliary

log = logging.getLogger(__name__)

class DroidBot(Auxiliary, Thread):
	"""
	DroidBot module
	A robot which interact with Android automatically
	"""
	def __init__(self):
		"""
		initiate droidbot instance
		"""
		Thread.__init__(self)
		self.output_dir = os.path.abspath("droidbot_out")
		if not os.path.exists(self.output_dir):
			os.mkdir(self.output_dir)

		self.device = Device(self.output_dir)
		self.app_path = adb.getLastInstalledPackagePath()
		self.app = App(self.app_path, self.output_dir)

		#Since we use the default environment, no need to deploy env_manager
		#self.env_manager = AppEnvManager(self.app)
		self.event_manager = AppEventManager(device = self.device, app = self.app)

	
	def run(self):
		log.info("Starting DroidBot")
		while not self.device.is_foreground(self.app):
			log.info("Waiting for app to be executed")
			time.sleep(2)

		try:
			self.event_manager.start()
		except KeyboardInterrupt:
			pass

		return True

	def stop(self):
		self.device.disconnect()
		self.event_manager.stop()
		log.info("Droidbot stopped")
		return


	