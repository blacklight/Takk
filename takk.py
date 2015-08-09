#!/usr/bin/env python2

from __future__ import print_function
from __armando__ import Armando
import os, re, sys, inspect, traceback

###
Armando.initialize()
###

from audiosource import AudioSource
from speechrecognition import SpeechRecognition, SpeechRecognitionError
from hue import Hue
from config import Config
from logger import Logger

class Takk():
    __config = Config.get_config()
    __logger = Logger.get_logger(__name__)

    def __init__(self):
        Takk.__logger.info({
            'msg_type': 'Application started',
            'config': Takk.__config.dump(),
        })

        self.audio = AudioSource()
        self.audio.record_to_flac()

        self.speech = SpeechRecognition()

        try:
            text, confidence = self.speech.recognize_speech_from_file()
        except SpeechRecognitionError as e:
            # TODO Properly manage the raised exception with a retry mechanism, see #13
            Takk.__logger.warning({
                'msg_type': 'Speech not recognized',
            })

            raise e

        self.hue = Hue()

        if re.search('play', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE):
            os.system('mpc play')

        if re.search('stop', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE):
            os.system('mpc pause')

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('on', text.lower(), re.IGNORECASE) \
              or \
            re.search('luci', text.lower(), re.IGNORECASE) and re.search('accend', text.lower(), re.IGNORECASE)):
            self.hue.connect()
            self.hue.set_on(True)

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('off', text.lower(), re.IGNORECASE) \
              or \
            re.search('luci', text.lower(), re.IGNORECASE) and re.search('spegn', text.lower(), re.IGNORECASE)):
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

