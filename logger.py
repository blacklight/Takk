import json
import logging

class Logger():
    """
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    __logger = None

    @classmethod
    def createStaticLogger(cls, logfile=None, loglevel='INFO'):
        cls.__logger = Logger(logfile=logfile, loglevel=loglevel)
        return cls.__logger

    @classmethod
    def getLogger(cls):
        return cls.__logger

    def __init__(self, logfile=None, loglevel='INFO'):
        if logfile is not None:
            self.logfile = logfile
        else:
            self.logfile = 'takk.log'

        if loglevel and loglevel.lower() == 'debug':
            self.loglevel = logging.DEBUG
        elif loglevel and loglevel.lower() == 'info':
            self.loglevel = logging.INFO
        elif loglevel and loglevel.lower() == 'warning':
            self.loglevel = logging.WARNING
        elif loglevel and loglevel.lower() == 'error':
            self.loglevel = logging.ERROR
        else:
            self.loglevel = logging.INFO

        logging.basicConfig(
            filename = self.logfile,
            level = self.loglevel,
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

