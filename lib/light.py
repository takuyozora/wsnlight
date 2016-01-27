# -*- coding: utf-8 -*-
# This module treat frames to send DMX data

import threading
import numpy as np
import ola.ClientWrapper
import math
import time


from settings import settings
from logger import init_log

log = init_log("dmx")


class DmxManager(object):
    """

    """

    def __init__(self, universe=0, dmxoutput_size=255):
        """
        :param universe:
        :param dmxoutput_size:
        :return:
        """
        self.universe = universe
        self.wrapper = ola.ClientWrapper.ClientWrapper()
        self.client = self.wrapper.Client()
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe
        self.dmxout = np.zeros(dmxoutput_size, dtype=np.uint8)
        log.info("DMX ready")

    def update_dmx(self):
        """
        :return:
        """
        log.debug("Update DMX {0}".format(self.dmxout[:len(settings.get("sensor", "addr"))]))
        self.client.SendDmx(self.universe, self.dmxout)

    def close(self):
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe


class DmxThread(threading.Thread):
    """
    This class represent the DMX thread
    """

    def __init__(self, universe=0, dmxoutput_size=255):
        """
        :param lightfile: reference to the lightfile object
        :param universe: DMX universe to use
        :param dmxoutput_size: Output size of the dmx array, reduce to a bit performance improving
        :return:
        """
        threading.Thread.__init__(self)
        self._must_close = threading.Event()
        self._must_close.clear()
        self.universe = universe
        self.wrapper = ola.ClientWrapper.ClientWrapper()
        self.client = self.wrapper.Client()
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe
        self.dmxout = np.zeros(dmxoutput_size, dtype=np.uint8)
        self.dt = 1/float(settings.get("dmx", "fps"))
        self.compute_all = None
        self.n_sensor = len(settings.get("sensor", "addr"))

    def run(self):
        """
        Main thread loop
        :return:
        """
        dt = 0
        drop = 0
        log.info("DMX ready")
        while self._must_close.isSet() is not True:
            if self.dt > dt + drop:
                time.sleep(self.dt - dt + drop)
                t = time.time()
                drop = 0
            else:
                log.warning("Drop frame")
                drop = (- self.dt + dt)*2
                t = time.time() - dt
            if self.compute_all is not None:
                self.compute_all()
                self.client.SendDmx(self.universe, self.dmxout)
                log.debug("DMX : {0}".format(self.dmxout[:self.n_sensor]))
            dt = time.time()-t
        self._on_close()

    def close(self):
        """
        :return:
        """
        self._must_close.set()

    def set_compute_all(self, compute_all):
        """
        Set comput all function
        :param compute_all: compute_all function
        :return:
        """
        self.compute_all = compute_all

    def _on_close(self):
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe