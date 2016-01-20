#!/bin/python2.7

from code.lib import logger
from code.lib.settings import settings
log = logger.init_log("test")
from code.lib import wsn
from code.lib import light

xbee = wsn.Xbee()
dmx = light.DmxManager()
sensors = wsn.SensorManager(tuple(settings.get("sensor", "addr")), dmx.dmxout)

try:
    if xbee.init():
        while True:
            sensors.recv_frame(xbee.get_frame())
            dmx.update_dmx()

except Exception:
    print("ERROR !")
finally:
    xbee.close()