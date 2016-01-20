#!/bin/python2
# -*- coding: utf-8 -*-

from lib import settings
settings.init("")

from lib import wsn
from lib import light
from lib import logger


settings = settings.settings
logger.SETTINGS = settings
log = logger.init_log("main", settings)

if __name__ == "__main__":
    try:
        xbee = wsn.Xbee()
        dmx = light.DmxManager()
        sensors = wsn.SensorManager(tuple(settings.get("sensor", "addr")), dmx.dmxout)
        if xbee.init():
            while True:
                sensors.recv_frame(xbee.get_frame())
                dmx.update_dmx()
        else:
            log.error("Can't init Xbee")
    except Exception:
        pass
    finally:
        xbee.close()
        dmx.close()