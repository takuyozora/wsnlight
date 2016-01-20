#!/bin/python2
# -*- coding: utf-8 -*-

import time

from lib import settings
settings.init()

from lib import wsn
from lib import light
from lib import logger


settings = settings.settings
logger.SETTINGS = settings
log = logger.init_log("main", settings)
dt = 1 / float(settings.get("dmx", "fps"))

if __name__ == "__main__":
    try:
        xbee = wsn.Xbee()
        dmx_th = light.DmxThread()
        sensor_th = wsn.SensorThread(xbee, dmx_th.dmxout)
        dmx_th.set_compute_all(sensor_th.sensors.compute_all)
        #sensors = wsn.SensorManager(tuple(settings.get("sensor", "addr")), dmx.dmxout)
        if xbee.init():
            sensor_th.start()
            dmx_th.start()
            while True:
                time.sleep(0.05)
        else:
            log.error("Can't init Xbee")
    except KeyboardInterrupt as e:
        print(str(e))
    finally:
        sensor_th.close()
        dmx_th.close()

