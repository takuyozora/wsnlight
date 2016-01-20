# -*- coding: utf-8 -*-
#

import serial
import threading
import time
import numpy as np

import mtools

from settings import settings
import logger
log = logger.init_log("wsn")


class Xbee(object):
    """
    This class represent the Xbee module
    """

    def __init__(self, serial_path=None, ATMY=None, ATID=None, ATCH=None, ATBD=None):
        """
        This method initiate the Xbee object but not the Xbee
        :return:
        """
        self._lock_serial = threading.Lock()
        if serial_path is None:
            serial_path = str(settings.get("xbee", "serial"))
        if ATBD is None:
            ATBD = str(settings.get("xbee", "ATBD"))
        if ATCH is None:
            ATCH = str(settings.get("xbee", "ATCH"))
        if ATID is None:
            ATID = str(settings.get("xbee", "ATID"))
        if ATMY is None:
            ATMY = str(settings.get("xbee", "ATMY"))
        self._serial = serial.Serial(serial_path, settings.get("xbee", "baudrates")[int(ATBD)])
        self._conf = {
            "ATMY": ATMY,
            "ATID": ATID,
            "ATCH": ATCH,
            "ATBD": ATBD
        }
        self._have_been_init = False
        self._conf_mode = False

    def close(self):
        """
        Ask to close the Xbee module
        :return:
        """
        if not self._conf_send("ATRE\r"):
            log.warning("Can't reset Xbee config before closing")
        self._serial.close()
        log.debug("Xbee serial close")

    def _conf_send(self, cmd, check=True, retry=True):
        """
        This methode send a command to the XBee and wait for a OK\r
        :param cmd: command to send
        :param check: True if wait a OK response
        :return:
        """
        if cmd != "+++" and not self._conf_mode:
                log.debug("need to be in conf mode, goto")
                while not self._conf_send("+++"):
                    time.sleep(1.1)
        elif cmd == "CN\r":
            self._conf_mode = False
        with self._lock_serial:
            log.debug("send : {0}, conf {1}".format(cmd, self._conf_mode))
            self._serial.write(cmd)
            b = 0
            r = ''
            if check is False:
                return True
            while b != '\r' and b != '\n':
                b = self._serial.read(1)
                r = r + b
            if r[-3:] != "OK\r":
                log.warning("!!! XBEE NOT OK !!! : {0}".format(str(r)))
                self._conf_mode = False
                if not retry:
                    return False
            elif cmd == "+++":
                self._conf_mode = True
                time.sleep(1.1)
                return True
            else:
                return True
        return self._conf_send(cmd, check, retry)

    def init(self):
        """
        This methode send the current configuration to the Xbee
        :return:
        """
        succes = True
        for key,value in self._conf.items():
            if not self._conf_send(key+str(value)+"\r"):
                succes = False
                break
        if succes:
            if self._conf_send("CN"+"\r", check=False):
                log.info("XBEE: INIT OK")
                self._have_been_init = True
                return True
        log.warning("XBEE: !FAIL INIT!")
        return False

    def get_frame(self):
        """
        This method wait a frame and return it
        :return:
        """
        with self._lock_serial:
            inframe = False
            frame = ""
            while True:
                r = self._serial.read(1)
                log.raw("inframe : read {0}".format(r))
                if inframe:
                    if r == "/":
                        print("Frame conflict")
                        inframe = False
                    elif r == "\\":
                        return SensorFrame(frame)    # print("Frame : {0}".format(frame))
                        # inframe = False
                    else:
                        frame += r
                else:
                    if r == "/":
                        inframe = True
                if not inframe:
                    frame = ""


class SensorManager(object):
    """

    """

    def __init__(self, sensor_addr, dmx_output):
        """
        :param sensor_addr: tuple of address
        :return:
        """
        self.sensors = dict()
        self.n_sensors = len(sensor_addr)
        self.dmx_output = dmx_output
        i = 0
        for addr in sensor_addr:
            self.sensors[int(addr)] = SensorValues(10, i)
            i += 1

    def recv_frame(self, frame):
        """
        :param frame: frame object
        :return:
        """
        if int(frame.src) not in self.sensors.keys():
            log.warning("Ignore frame {0} because addr not configure {1}".format(frame, self.sensors.keys()))
            return False
        log.debug("Add {0} in {1}".format(frame.val, frame.src))
        sens =self.sensors[int(frame.src)]
        #self.sensors[int(frame.src)].put_data(int(frame.val))
        sens.put_data(int(frame.val))
        self.dmx_output[sens.addr] = sens.compute()



class SensorThread(threading.Thread):
    """
    Class which recv sensorframes and keep a value table up to date
    """

    def __init__(self, n_sensor):
        """
        :param n_sensor: number of sensor
        :return:
        """

class SensorValues(object):
    """
    Class which transform raw data to DMX value
    """

    def __init__(self, depth, addr):
        """
        :param depth: Depth of data to store
        :param addr: dmx_addr
        :return:
        """
        self._buffer = mtools.CircularBuffer(depth)
        self.addr = addr
        self._sum_depth = depth
        self._factor = float(settings.get("dmx", "max_value"))/(depth * int(settings.get("sensor", "max_value")))

    def put_data(self, data):
        """
        Put data in the buffer
        :param data:
        :return:
        """
        self._buffer.put(data)

    def compute(self):
        """
        Compute current value
        :return:
        """
        return int(np.sum(self._buffer.data[:self._sum_depth]) * float(self._factor))

class SensorFrame(object):
    """
    This class represent a frame recv by the coordinator
    """

    def __init__(self, raw_frame):
        """
        :param raw_frame: string of the raw frame, ex : "/3,123\"
        :return:
        """
        self._raw = raw_frame
        self.src, self.val = raw_frame.split(",")

    def __repr__(self):
        return "addr:{0}, val:{1}, raw:{2}".format(self.src, self.val, self._raw)

    def __str__(self):
        return self.__repr__()


