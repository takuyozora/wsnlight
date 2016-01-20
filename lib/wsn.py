# -*- coding: utf-8 -*-
#

import serial
import threading

BAUDRATES = (
    0,
    2400,
    4800,
    9600,
    19200,
    38400,
    57600,
    115200
)


class Xbee(object):
    """
    This class represent the Xbee module
    """

    def __init__(self, serial_path="/dev/ttyAMA0", ATMY="3210", ATID="1111", ATCH="0C", ATBD="5"):
        """
        This method initiate the Xbee object but not the Xbee
        :return:
        """
        self._lock_serial = threading.Lock()
        self._serial = serial.Serial(serial_path, BAUDRATES[int(ATBD)])
        self._conf = {
            "ATMY": ATMY,
            "ATID": ATID,
            "ATCH": ATCH,
            "ATBD": ATBD
        }
        self._have_been_init = False

    def close(self):
        self._serial.close()

    def _conf_send(self, cmd):
        """
        This methode send a command to the XBee and wait for a OK\r
        :param cmd: command to send
        :return:
        """
        with self._lock_serial:
            self._serial.write(cmd)
            b = 0
            r = ''
            while b != '\r' and b != '\n':
                b = self._serial.read(1)
                r = r + b
            if r[:2] != "OK":
                print("!!! XBEE NOT OK !!!")
                return False
            return True

    def init(self):
        """
        This methode send the current configuration to the Xbee
        :return:
        """
        succes = True
        if not self._conf_send("+++"):
            succes = False
        else:
            for key,value in self._conf.items():
                if not self._conf_send(key+str(value)+"\r"):
                    succes = False
                    break
        if succes:
            if self._conf_send("CN"+"\r"):
                print("XBEE: INIT OK")
                self._have_been_init = True
                return True
        print("XBEE: !FAIL INIT!")
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
            if inframe:
                if r == "/":
                    print("Frame conflict")
                    inframe = False
                elif r == "\\":
                    return frame    # print("Frame : {0}".format(frame))
                    # inframe = False
                else:
                    frame += r
            else:
                if r == "/":
                    inframe = True
            if not inframe:
                frame = ""
