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
        self._serial = serial.Serial(serial_path, settings.get("xbee", "baudrates")[int(ATBD)], timeout=1)
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
        :param retry: True if auto retry to send the command if failled
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
                b = ""
                while len(b) == 0:  # Ignore timeout
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
        for key, value in self._conf.items():
            if not self._conf_send(key + str(value) + "\r"):
                succes = False
                break
        if succes:
            if self._conf_send("CN" + "\r", check=False):
                log.info("XBEE: INIT OK")
                self._have_been_init = True
                return True
        log.warning("XBEE: !FAIL INIT!")
        return False

    def get_frame(self):
        """
        This method wait a frame and return it
        :return: False if timeout reached
        """
        with self._lock_serial:
            inframe = False
            frame = ""
            while True:
                r = self._serial.read(1)
                if len(r) == 0:  # Timeout occured
                    return False
                if inframe:
                    if r == "/":
                        log.warning("Frame conflict")
                        inframe = False
                    elif r == "\\":
                        return SensorFrame(frame)
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
            self.sensors[int(addr)] = SensorValues(i)
            i += 1

    def compute_all(self):
        """
        Compute all sensors
        :return:
        """
        for addr, sensor in self.sensors.items():
            self.dmx_output[sensor.addr] = sensor.compute()

    def recv_frame(self, frame):
        """
        :param frame: frame object
        :return:
        """
        if int(frame.src) not in self.sensors.keys():
            log.warning("Ignore frame {0} because addr not configure {1}".format(frame, self.sensors.keys()))
            return False
        log.raw("Add {0} in {1}".format(frame.val, frame.src))
        sens = self.sensors[int(frame.src)]
        # self.sensors[int(frame.src)].put_data(int(frame.val))
        sens.put_data(int(frame.val))
        # self.dmx_output[sens.addr] = sens.compute()


class SensorThread(threading.Thread):
    """
    Class which recv sensorframes and keep a value table up to date
    """

    def __init__(self, xbee, dmxout):
        """
        :param n_sensor: number of sensor
        :return:
        """
        threading.Thread.__init__(self)
        self._must_stop = threading.Event()
        self._must_stop.clear()
        self.xbee = xbee
        self.sensors = SensorManager(tuple(settings.get("sensor", "addr")), dmxout)
        self._config_addr = str(settings.get("reconfig_addr"))

    def run(self):
        """
        Main loop of thread
        :return:
        """
        while self._must_stop.isSet() is not True:
            frame = self.xbee.get_frame()
            log.raw("get {0}".format(frame))
            if frame is False:
                continue
            elif str(frame.src) == self._config_addr:
                log.debug("Reconfig {0}".format(frame.val))
            else:
                self.sensors.recv_frame(frame)
        self.xbee.close()

    def close(self):
        """
        Ask thread to stop
        :return:
        """
        self._must_stop.set()


class SensorValues(object):
    """
    Class which transform raw data to DMX value
    """

    def __init__(self, addr):
        """
        :param addr: dmx_addr
        :return:
        """
        self._sum_depth = float(settings.get("sensor", "depth")) * int(settings.get("dmx", "fps"))
        self._buffer = mtools.CircularBuffer(self._sum_depth)
        self.addr = addr
        self._uptodate = 0
        self._auto_fall_threshold = float(settings.get("dmx", "fps")) * float(settings.get("sensor", "auto_fall"))
        self._cache = 0
        self._factor = float(settings.get("dmx", "max_value")) / (
                       self._sum_depth * ( int(settings.get("sensor", "max_value")) - int(settings.get("sensor", "min_value")) ))
        self.min_val = int(settings.get("sensor", "min_value"))

        log.debug("facotr {0}, min_val {1} !".format(self._factor, self.min_val))

    def put_data(self, data):
        """
        Put data in the buffer
        :param data:
        :return:
        """
        self._uptodate = 0
        d = data - self.min_val
        if d < 0:
            log.raw("Put 0 in buffer {0} (sat)".format(self.addr))
            self._buffer.put(0)
        else:
            log.raw("Put {0} in buffer {1}".format(d, self.addr))
            self._buffer.put(d)

    def _compute(self):
        """
        :return: Value to send to the DMX channel
        """
        v = int((np.sum(self._buffer.data[:self._sum_depth])) * float(self._factor))
        if v < 0:
            return 0
        else:
            return v

    def compute(self):
        """
        Compute current value for the DMX channel
        :return:
        """
        if self._uptodate > 0:      # There is no new value in the buffer
            if self._uptodate > self._auto_fall_threshold:          # It has been too long since the last value : start auto-fall
                self._buffer.put(int(self._cache/self._uptodate))   # Add a lower value to the buffer
                self._cache = self._compute()                       # Compute new value
            else:
                log.raw("Use buffer {0}, {1}".format(self.addr,self._cache))
            self._uptodate += 1     # Increment uptodate to know since when there haven't been a new value
            return self._cache
        else:                       # There at least a new value in the buffer
            self._uptodate = 1      # Set uptodate to one to signify that the buffer and the cache are sync
            self._cache = self._compute()
            log.raw("Compte new value {0}, {1}".format(self.addr,self._cache))
            return self._cache


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
        try:
            self.src, self.val = raw_frame.split(",")
        except ValueError:
            log.warning("Corrupted frame : skip")

    def __repr__(self):
        return "addr:{0}, val:{1}, raw:{2}".format(self.src, self.val, self._raw)

    def __str__(self):
        return self.__repr__()
