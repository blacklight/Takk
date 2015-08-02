from __future__ import print_function

try:
    from configparser import ConfigParser
except ImportError as e:
    from ConfigParser import ConfigParser

import json
import os
import re
import sys

class ConfigError(Exception):
    pass

class Config():
    """
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    def __init__(self, rcfile=None):
        """
        @param rcfile Path string to the configuration file (default: first ~/.takkrc then ./takkrc)
        """
        if rcfile is None:
            self.rcfile = os.getenv('HOME') + '/.takkrc'
            if not os.path.isfile(self.rcfile):
                self.rcfile = './takkrc'
        else:
            self.rcfile = rcfile

        self.parser = ConfigParser()
        self.config = {}

        try:
            self.parser.readfp(open(self.rcfile))
        except Exception as e:
            raise e

        for section in self.parser.sections():
            for opt in self.parser.items(section):
                key = '%s.%s' % (section, opt[0])
                value = opt[1]
                self.config[key] = value

    def get(self, attr):
        return self.config[attr]

    def dump(self):
        return json.dumps(self.config)

# vim:sw=4:ts=4:et:

