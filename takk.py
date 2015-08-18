#!/usr/bin/env python

from __future__ import print_function
from __armando__ import Armando
import json, os, re, sys, inspect, traceback

###
Armando.initialize()
###

from audiosource import AudioSource
from speechrecognition import SpeechRecognition, SpeechRecognitionError
from hue import Hue
from mpd import MPD
from config import Config
from logger import Logger
from rules import Rules

class Takk():
    __config = Config.get_config()
    __logger = Logger.get_logger(__name__)
    __takk_basedir = Armando.get_base_dir() + os.sep + 'share' + os.sep + 'Takk'

    def __init__(self):
        self.__logger.info({
            'msg_type': 'Application started',
            'config': self.__config.dump(),
        })

        audio = AudioSource()
        audio.record_to_flac()

        speech = SpeechRecognition()

        try:
            text, confidence = speech.recognize_speech_from_file()
            self.__logger.info({
                'msg_type': 'Speech recognized',
                'text': text,
                'confidence': confidence,
            })

        except SpeechRecognitionError as e:
            # TODO Properly manage the raised exception with a retry mechanism, see #13
            self.__logger.info({
                'msg_type': 'Speech not recognized',
            })

        rules = Rules(self.__takk_basedir + os.sep + 'rules.xml')
        patterns = rules.pattern_match(text.strip())

        if len(patterns) == 0:
            self.__logger.info({
                'msg_type': 'No pattern matched',
                'text': text,
            })
        else:
            self.__logger.info({
                'msg_type': 'Pattern matched',
                'text': text,
                'patterns': json.dumps(patterns),
            })

        if (re.search('play', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE) \
                or \
                re.search('musica', text.lower(), re.IGNORECASE) and re.search('avvia', text.lower(), re.IGNORECASE)):
            self.mpd = MPD()
            self.mpd.server_cmd('play')

        if (re.search('stop', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE) \
                or \
                re.search('musica', text.lower(), re.IGNORECASE) and re.search('spegni', text.lower(), re.IGNORECASE)):
            self.mpd = MPD()
            self.mpd.server_cmd('pause')

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('on', text.lower(), re.IGNORECASE) \
                or \
                re.search('luci', text.lower(), re.IGNORECASE) and re.search('accend', text.lower(), re.IGNORECASE)):
            self.hue = Hue()
            self.hue.connect()
            self.hue.set_on(True)

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('off', text.lower(), re.IGNORECASE) \
                or \
                re.search('luci', text.lower(), re.IGNORECASE) and re.search('spegn', text.lower(), re.IGNORECASE)):
            self.hue = Hue()
            self.hue.connect()
            self.hue.set_on(False)

if __name__ == '__main__':
    try:
        Takk()
    except Exception as e:
        tb = traceback.format_exc()
        Logger().error({
            'msg_type'   : 'Uncaught exception, exiting',
            'exception' : tb,
        })

        raise e

# vim:sw=4:ts=4:et:

