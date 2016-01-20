#!/bin/python2.7

from code.lib import logger
log = logger.init_log("test")
from code.lib import wsn

xbee = wsn.Xbee()

try:
    if xbee.init():
        while True:
            print(xbee.get_frame())

except Exception:
    print("ERROR !")
finally:
    xbee.close()
