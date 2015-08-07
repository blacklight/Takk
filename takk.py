#!/usr/bin/env python

from __future__ import print_function
from __armando__ import Armando
import os, re, sys, inspect

###
Armando.initialize()
###

from audiosource import AudioSource
from speechrecognition import SpeechRecognition, SpeechRecognitionError
from hue import Hue
from config import Config
from logger import Logger

class App():
    def __init_logging(self):
        self.log = Logger.create_static_logger(
            logfile=os.path.expanduser(self.config.get('log.logfile')),
            loglevel=self.config.get('log.loglevel'),
        )

        self.log.info({
            'msg_type': 'Application started',
            'module': self.__class__.__name__,
            'config': self.config.dump(),
        })

    def __get_audio_source(self):
        return AudioSource(
            audio_file=self.config.get('audio.audio_file'),
            threshold=self.config.get('audio.threshold'),
            chunk_size=self.config.get('audio.chunk_size'),
            rate=self.config.get('audio.rate'))

    def __get_speech_recognition(self):
        return SpeechRecognition(
            api_key=self.config.get('speech.google_speech_api_key'),
            languages=self.config.get('speech.language').split(',')
        )

    def __init__(self):
        self.config = Config()
        self.__init_logging()

        self.audio = self.__get_audio_source()
        self.audio.record_to_file()

        self.speech = self.__get_speech_recognition()

        try:
            text, confidence = self.speech.recognize_speech_from_file(filename=self.config.get('audio.audio_file'))
            os.remove(self.config.get('audio.audio_file'))
        except SpeechRecognitionError as e:
            # TODO Properly manage the raised exception with a retry mechanism, see #13
            self.log.warning({
                'msg_type': 'Speech not recognized',
                'module': self.__class__.__name__,
            })

            raise e

        hue = Hue(bridge=self.config.get('hue.bridge'))

        if re.search('play', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE):
            os.system('mpc play')

        if re.search('stop', text.lower(), re.IGNORECASE) and re.search('music', text.lower(), re.IGNORECASE):
            os.system('mpc pause')

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('on', text.lower(), re.IGNORECASE) \
              or \
            re.search('luci', text.lower(), re.IGNORECASE) and re.search('accend', text.lower(), re.IGNORECASE)):
            hue.connect()
            hue.set_on(True)

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('off', text.lower(), re.IGNORECASE) \
              or \
            re.search('luci', text.lower(), re.IGNORECASE) and re.search('spegn', text.lower(), re.IGNORECASE)):
            hue.connect()
            hue.set_on(False)

if __name__ == '__main__':
    try:
        App()
    except BaseException as e:
        Logger().error({
            'msg_type'   : 'Uncaught exception, exiting',
            'exception' : str(e),
        })

        raise e

# vim:sw=4:ts=4:et:

