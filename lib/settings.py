# -*- coding: utf-8 -*-
#
# This file load settings and can modify them
#   Settings are store in a JSON file
#

import sys
import os
import json
# Import log #
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
import logger

#
log = logger.init_log("setting", settings={"log": dict()}, log_type="Console")

VERSION = 1.0

_DEFAULT_SETTING = dict()
_DEFAULT_SETTING["log"] = dict()
_DEFAULT_SETTING["log"]["level"] = "info"
_DEFAULT_SETTING["log"]["output"] = "Console"

_DEFAULT_SETTING["xbee"] = dict()
_DEFAULT_SETTING["xbee"]["baudrates"] = (
    0,
    2400,
    4800,
    9600,
    19200,
    38400,
    57600,
    115200
)
_DEFAULT_SETTING["xbee"]["serial"] = "/dev/ttyAMA0"
_DEFAULT_SETTING["xbee"]["ATBD"] = "3"
_DEFAULT_SETTING["xbee"]["ATCH"] = "0C"
_DEFAULT_SETTING["xbee"]["ATID"] = "1111"
_DEFAULT_SETTING["xbee"]["ATMY"] = "3210"

_DEFAULT_SETTING["reconfig_addr"] = "15"

_DEFAULT_SETTING["sensor"] = dict()
_DEFAULT_SETTING["sensor"]["depth"] = 3             # in sec
_DEFAULT_SETTING["sensor"]["addr"] = (19, 20)
_DEFAULT_SETTING["sensor"]["max_value"] = 1024
_DEFAULT_SETTING["sensor"]["auto_fall"] = 0.5       # in sec

_DEFAULT_SETTING["dmx"] = dict()
_DEFAULT_SETTING["dmx"]["max_value"] = 255
_DEFAULT_SETTING["dmx"]["fps"] = 30




class Settings(dict):
    """
    This class old settings
    """

    def __init__(self, path, default=dict()):
        """
        :param path: path to the settings file
        :return:
        """
        self._path = path
        self._default = default
        dict.__init__(self, default)
        if path is "":
            log.info("No settings file given, do not create one")
        else:
            try:
                with open(path, 'r') as fp:
                    try:
                        self.update(json.load(fp))
                    except:
                        log.error("Could not load settings")
            except IOError:
                log.info("No settings found at path {0}, create one".format(path))
                if default != {}:  # If there is some default settings
                    try:
                        with open(path, 'wr') as fp:  # Create setting file
                            pass
                        self.save()  # Write settings on disk
                    except (IOError, OSError) as e:
                        log.error("Could not create defauflt setting file, skip")
            except json.scanner.JSONDecodeError as e:
                log.error("Could not load settings : {0}".format(e))

    def save(self):
        return self._save(self._path, "w")

    def save_as(self, path):
        return self._save(path, "a")

    def _save(self, path, mode):
        with open(path, mode) as fp:
            json.dump(self, fp)

    def __getitem__(self, item):
        if item not in self.keys():
            return self._default[item]
        return dict.__getitem__(self, item)

    def get_default(self, *args):
        """
        Return the default value, act as get but for the default dictionnarie
        :param args:
        :return:
        """
        d = self._default
        for elem in args:
            d = d[elem]
        return d

    def get(self, *args):
        """
        Return the correct value
        :param args: path to the setting (ex: ("OSC", "ackport"))
        :return:
        """
        d = self
        for elem in args:
            if elem in d.keys():
                d = d[elem]
            else:
                return self.get_default(*args)
        return d

    def get_path(self, *args):
        """
        This function return a path based on settings with ("path","main") as root path
        :param args: each relative path to cross
        :return:
        """
        if args[0] not in self.get("path", "relative").keys():
            return self.get("path", *args)
        abs_path = self.get("path", "main")
        for path in args:
            abs_path = os.path.join(abs_path, settings.get("path", "relative", path))
        return abs_path

#settings = Settings("", _DEFAULT_SETTING)

def init(settings_path=None, default_settings=None):
    """
    This function initialized setting module
    :param settings_path: path to the setting JSON file
    :type settings_path: str
    :param default_settings: default settings used if JSON file don't define them
    :type default_settings: dict
    :return: None
    """
    global settings
    if settings_path is None:
        settings_path = os.path.expanduser("~/.wsnlight.conf")
    if default_settings is None:
        default_settings = _DEFAULT_SETTING
    settings = Settings(settings_path, default_settings)
    logger.SETTINGS = settings
    log.debug(settings)
