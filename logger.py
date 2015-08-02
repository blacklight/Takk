import json
import logging
import os

class Logger():
    """
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    __logger = None

    @classmethod
    def createStaticLogger(cls, logfile=None):
        cls.__logger = Logger(logfile)
        return cls.__logger

    @classmethod
    def getLogger(cls):
        return cls.__logger

    def __init__(self, logfile=None):
        if logfile is not None:
            self.logfile = logfile
        else:
            basedir = os.getenv('HOME') + '/.takk'
            if not os.path.isdir(basedir):
                os.mkdir(basedir)
            self.logfile = '%s/takk.log' % basedir

        logging.basicConfig(
            filename = self.logfile,
            level = logging.DEBUG,
            format = '[%(asctime)-15s] %(message)s'
        )

    def debug(self, msg):
        logging.debug(json.dumps(msg))

    def info(self, msg):
        logging.info(json.dumps(msg))

    def warning(self, msg):
        logging.warning(json.dumps(msg))

    def error(self, msg):
        logging.error(json.dumps(msg))

# vim:sw=4:ts=4:et:

