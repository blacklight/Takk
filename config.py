from __future__ import print_function

try:
    from configparser import SafeConfigParser
except ImportError as e:
    from ConfigParser import SafeConfigParser

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
        @param rcfile Path string to the configuration file (default: ./takkrc)
        """
        if rcfile is None:
            self.rcfile = 'takkrc'
        else:
            self.rcfile = rcfile

        self.parser = SafeConfigParser()
        self.config = {}

        try:
            self.parser.readfp(open(self.rcfile))
        except Exception as e:
            raise e

        for section in self.parser.sections():
            for opt in self.parser.items(section):
                key = ('%s.%s' % (section, opt[0])).lower()
                value = opt[1]
                self.config[key] = value

    def get(self, attr):
        attr = attr.lower()
        if attr == 'speech.google_speech_api_key':
            return self.config[attr] if attr in self.config else os.getenv('GOOGLE_SPEECH_API_KEY')
        return self.config[attr] if attr in self.config else None

    def dump(self):
        return json.dumps(self.config)

# vim:sw=4:ts=4:et:

