# -*- coding: utf-8 -*-
# This module treat frames to send DMX data

import threading
import numpy as np
import ola.ClientWrapper
import math



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
        self.universe = universe
        self.wrapper = ola.ClientWrapper.ClientWrapper()
        self.client = self.wrapper.Client()
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe
        self.dmxout = np.zeros(dmxoutput_size, dtype=np.uint8)

    def do_msg(self, msg):
        """
        Compute all dmx
        :param msg:
        :return:
        """
        #self.log.raw("tick dmx")
        frame = self.get_current_frame()
        for spot in self.lightfile.spots:
            spot.update_dmx(frame, 1)
        #self.log.raw("dmx out put {0}".format(self.dmxout))
        self.client.SendDmx(self.universe, self.dmxout)

    def _on_close(self):
        self.client.SendDmx(self.universe, np.zeros(255, dtype=np.uint8))  # Clean all the universe