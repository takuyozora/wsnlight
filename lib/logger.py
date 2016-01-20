# -*- coding: utf-8 -*-
#
# This file provide a simple log system
#
#
"""
Provides a simple wrapper around the python logger.

Right now there is the base Log class, and three specialized classes that
inherit from the Log class: ConsoleLog, FileLog, and DualLog.  ConsoleLog logs
messages to the standard output (command line), FileLog outputs to a log file,
and DualLog outputs to both.

The programmer does not need to think about the logger types because this will
be specified in the user's settings.  So to set up your module to log do the
following:

Usage:
    from src.log import Log

    log = Log("my.module")
    log.debug("a debug message")

"""

import os
import sys
import traceback

import logging
import logging.handlers


LEVELS = {
    "net": logging.DEBUG - 5,
    "raw": logging.DEBUG - 3,
    "step": logging.DEBUG - 2,
    "flow": logging.DEBUG - 1,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
for _level, _lvl_value in LEVELS.items():
    logging.addLevelName(_lvl_value, _level.upper())

DEFAULT_LEVEL = "debug"
DEFAULT_LOG_TYPE = "Console"
LOG_PATH = os.path.join("/tmp/", "logger.log")
SETTINGS = None

SETTINGS = dict()
SETTINGS["log"] = dict()
SETTINGS["log"]["level"] = "info"
SETTINGS["log"]["output"] = "Console"

# The following merely sets the log type/level if it hasn't already been set
changed = False
if DEFAULT_LEVEL not in LEVELS:
    DEFAULT_LEVEL = "debug"
    # settings.set("logging", "level", DEFAULT_LEVEL.title())
    changed = True

if not DEFAULT_LOG_TYPE:
    DEFAULT_LOG_TYPE = "Console"
    # settings.set("logging", "type", DEFAULT_LOG_TYPE)
    changed = True

# if changed:
# settings.write()

MAX_FUNC_NAME = 20  # Max func name length

if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "a").close()
# DEFAULT_FORMAT = "%(message)s"
# FILE_FORMAT = "%(asctime)s %(levelname)s\t%(name)s\t%(message)s"
# CONSOLE_FORMAT = "%(levelname)s\t\t%(name)s\t%(message)s"
# DEFAULT_FORMAT = "%(levelname)-9s%(name)-10s%(funcName)s%(message)s"
DEFAULT_FORMAT = "%(asctime)s\t%(levelname)-9s%(name)-10s%(funcName)s%(message)s"
# FORMAT_DEBUG = "                        `-> In %(filename)s at line %(lineno)d"
# ALL_FORMAT = DEFAULT_FORMAT + "\n" + FORMAT_DEBUG
ALL_FORMAT = "%(asctime)s\t%(levelname)-9s%(name)-10s%(fnamelineo)-40s%(message)s"

TRICK_LOG = logging.Logger("/!\\TRICK_LOG see log.py/!\\")


def makeRecord(name, lvl, fn, lno, msg, args, exc_info, func=None, extra=None):
    f = sys._getframe(4)
    fname = f.f_code.co_filename
    flineo = f.f_lineno
    funcname = f.f_code.co_name
    return logging.Logger.makeRecord(TRICK_LOG, name, lvl, fname, flineo, msg, args, exc_info,
                                     str("{:<" + str(MAX_FUNC_NAME) + "}").format("[" + funcname + "]"),
                                     extra={"fnamelineo": os.path.basename(fname) + ":" + str(
                                         flineo) + " [" + funcname + "]"})


class BaseLog:
    """
    Provides a wrapper around the logging module to simplify some logging tasks.
    This base class should generally not be called.

    """

    def __init__(self, logger="", level=None):
        if level is None:
            level = DEFAULT_LEVEL
        self.logger = logging.getLogger(logger)
        self.level = level
        self.logger.setLevel(LEVELS[level])
        self.logger.makeRecord = makeRecord
        self.handler = None
        # self.debug("Start log system with "+level.upper()+" level")

    def __call__(self, *args, **kwargs):
        return self.debug(*args, **kwargs)

    def show_exception(self, exception):
        """
        Get full information abour an exception
        :param exception:
        :return: string
        """
        return str(traceback.format_exc()) + str(sys.exc_info()[0])

    # @staticmethod
    # def get_frame_info(depth=2):
    # f = sys._getframe(depth)
    #     code = f.f_code
    #     d = {}
    #     d["_fname"] = code.co_name
    #     d["_lnum"] = f._lineno
    #     d["_filename"] = code.co_filename
    #     return d

    def set_level(self, level=DEFAULT_LEVEL):
        """
        Set the mimimum level to be logged.

        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical)

        """

        self.level = level
        self.logger.setLevel(LEVELS[level])

    def isEnabledFor(self, lvl):
        """
        Return True if the lvl is enable for output
        :param lvl:
        :return:
        """

        return self.logger.isEnabledFor(lvl)

    def log(self, lvl, msg):
        """
        Emit a custom lvl message
        :param lvl: type(str) name of the lvl
        :param msg: type(str) msg to log
        :return:
        """
        try:
            self.logger.log(LEVELS[lvl], msg)
        except KeyError:
            self.debug("Level name " + str(lvl) + " unknown. Message : " + str(msg))

    def debug(self, msg=""):
        """
        Pass a debug level log message (Numeric value: 10)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.debug(msg)

    def raw(self, msg=""):
        """
        Pass an info level log message (Numeric value: 20)

        @type   msg: string
        @param  msg: The message to pass

        """

        try:
            self.logger.log(LEVELS['raw'], msg)
        except KeyError:
            self.debug("Level name " + 'raw' + " unknown. Message : " + str(msg))

    def info(self, msg=""):
        """
        Pass an info level log message (Numeric value: 20)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.info(msg)

    def warning(self, msg=""):
        """
        Pass a warning level log message (Numeric value: 30)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.warning(msg)

    def error(self, msg=""):
        """
        Pass an error level log message (Numeric value: 40)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.error(msg)

    def critical(self, msg=""):
        """
        Pass a critical level log message (Numeric value: 50)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.critical(msg)

    def exception(self, msg=""):
        """
        Pass a exception level log message (Numeric value: 50)

        @type   msg: string
        @param  msg: The message to pass

        """

        self.logger.exception(msg)

    def exception_info(self, msg, exc_info):
        """
        Pass an exception info tuple (as per sys.exc_info() format, (type,
        value, traceback).

        @type exc_info: (type, value, traceback)
        @param exc_info: exception info
        """
        self.logger.debug(msg, exc_info=exc_info)

    def set_handler(self, handler, format=DEFAULT_FORMAT):
        """
        Set how the logging module should handle log messages.

        @type   handler: logging.Handler
        @param  handler: The class that handles log messages

        @type   format: string
        @param  format: The formatting to be used when displaying messages

        """

        self.handler = handler
        self.handler.setLevel(LEVELS[self.level])
        self.handler.setFormatter(logging.Formatter(format))
        self.logger.addHandler(self.handler)


class ConsoleLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to the
    command line/standard output.

    Usage:
        clog = ConsoleLog("rabbitvcs.ui.commit")
        clog.debug("This function needs refactoring")
        clog.error("You just screwed the pooch!")

    """

    def __init__(self, logger="", level=None, format=DEFAULT_FORMAT):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages

        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical)

        """

        BaseLog.__init__(self, logger, level)
        self.set_handler(logging.StreamHandler(), format)


class FileLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to file
    which is automatically rotated every day and keeps seven days worth of data.

    Usage:
        flog = FileLog("rabbitvcs.ui.commit")
        flog.debug("This function needs refactoring")
        flog.error("You just screwed the pooch!")

    """

    def __init__(self, logger="", level=None, format=DEFAULT_FORMAT, log_path=LOG_PATH):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages

        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical)

        """

        BaseLog.__init__(self, logger, level)
        self.set_handler(
            logging.handlers.TimedRotatingFileHandler(log_path, "D", 1, 7, "utf-8"),
            ALL_FORMAT
        )


class DualLog(BaseLog):
    """
    Inherits from BaseLog and provides a simple interface to log calls to both the
    command line/standard output and a file which is automatically rotated every
    day.

    Usage:
        dlog = DualLog("rabbitvcs.ui.commit")
        dlog.debug("This function needs refactoring")
        dlog.error("You just screwed the pooch!")

    """

    def __init__(self, logger="", level=None, format=DEFAULT_FORMAT, format_file=None, log_path=LOG_PATH):
        """
        @type   logger: string
        @param  logger: A keyword describing the source of the log messages

        @type   level: string
        @param  level: The minimum level to log.  (debug, info, warning, error, critical)

        """

        BaseLog.__init__(self, logger, level)
        if format_file is None:
            format_file = format
        self.set_handler(
            logging.handlers.TimedRotatingFileHandler(log_path, "D", 1, 7, "utf-8"),
            format_file
        )
        self.set_handler(logging.StreamHandler(), format)


class NullHandler(logging.Handler):
    """
    Handles log messages and doesn't do anything with them

    """

    def emit(self, record):
        pass


class NullLog(BaseLog):
    """
    If the user does not want to generate a log file, use the NullLog.  It calls
    the NullHandler class as its handler.

    """

    def __init__(self, *args, **kwargs):
        BaseLog.__init__(self, *args, **kwargs)
        self.set_handler(NullHandler())


Log = NullLog
if DEFAULT_LOG_TYPE == "File":
    Log = FileLog
elif DEFAULT_LOG_TYPE == "Console":
    Log = ConsoleLog
elif DEFAULT_LOG_TYPE == "Both":
    Log = DualLog


def set_Log(logger):
    global Log
    Log = logger


def set_log_type(set_type, path=None):
    if set_type not in ("Console", "File", "Both"):
        raise ValueError("Must be in {0}".format(("Console", "File", "Both")))
    global DEFAULT_LOG_TYPE
    DEFAULT_LOG_TYPE = set_type
    if set_type in ("File", "Both"):
        if path is None:
            return
        global LOG_PATH
        LOG_PATH = path


def _init_log(log_name, log_lvl=None, log_type=None, log_format=None, log_format_file=None, log_path=None):
    Log = None
    if log_lvl is None:
        log_lvl = DEFAULT_LEVEL
    if log_type is None:
        log_type = DEFAULT_LOG_TYPE
    if log_format is None:
        log_format = DEFAULT_FORMAT
    if log_format_file is None:
        log_format_file = ALL_FORMAT
    if log_path is None:
        log_path = LOG_PATH
    if log_type not in ("Console", "File", "Both", "Null"):
        raise ValueError("Must be in {0}".format(("Console", "File", "Both", "Null")))
    if log_type == "File":
        Log = FileLog(log_name, level=log_lvl, format=log_format, log_path=log_path)
    elif log_type == "Console":
        Log = ConsoleLog(log_name, level=log_lvl, format=log_format)
    elif log_type == "Both":
        Log = DualLog(log_name, level=log_lvl, format=log_format, format_file=log_format_file, log_path=log_path)
    elif log_type == "Null":
        Log = NullLog(log_name, level=log_lvl)
    Log.debug("=== START LOGGING ===")
    return Log


def init_log(log_name, settings=None, log_lvl=None, log_type=None, log_format=DEFAULT_FORMAT,
             log_format_file=ALL_FORMAT, log_path=None):
    if settings is None:
        settings = SETTINGS
    else:
        global SETTINGS
        SETTINGS = settings
    if settings is not None:
        if log_lvl is None and "level" in settings["log"].keys():
            log_lvl = settings["log"]["level"]
        if log_type is None and "output" in settings["log"].keys():
            log_type = settings["log"]["output"]
        if log_path is None and "path" in settings["log"].keys():
            log_path = settings["log"]["path"]
        if log_format is None and "format" in settings["log"].keys():
            log_format = settings["log"]["format"]
        if log_format_file is None and "format_file" in settings["log"].keys():
            log_format_file = settings["log"]["format_file"]
    else:
        raise RuntimeWarning("logger settings not init")
    return _init_log(log_name, log_lvl, log_type, log_format, log_format_file, log_path)