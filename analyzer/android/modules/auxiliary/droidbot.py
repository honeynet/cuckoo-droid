# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.
# Originally contributed by Check Point Software Technologies, Ltd.

import logging
import sys
import os
from threading import Thread
from lib.api.droidbot_types import App, Device
from lib.api.droidbot_env import AppEnvManager
from lib.api.droidbot_event import AppEventManager
from lib.api.adb import getLastInstalledPackagePath
from lib.common.abstracts import Auxiliary

log = logging.getLogger(__name__)

class DroidBot(Auxiliary):
	"""
	DroidBot module
	A robot which interact with Android automatically
	"""
	def __init__(self):
		"""
		initiate droidbot instance
		"""
		self.output_dir = os.path.abspath("droidbot_out")
		if not os.path.exists(self.output_dir):
			os.mkdir(self.output_dir)

		self.device = Device(self.output_dir)
		self.app_path = getLastInstalledPackagePath()
		self.app = App(self.app_path, self.output_dir)

		#Since we use the default environment, no need to deploy env_manager
		#self.env_manager = AppEnvManager(self.app)
		self.event_manager = AppEventManager(device = self.device, app = self.app)

	"""
	def run(self):
		log.info("Starting DroidBot")
		try:
			#self.env_manager.deploy()
			self.event_manager.start()
		except:
			pass

		self.stop()
		log.info("DroidBot stopped")

	def stop(self):
		#self.env_manager.stop()
		self.event_manager.stop()


	"""