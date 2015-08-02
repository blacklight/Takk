#!/usr/bin/env python

from __future__ import print_function

from audiosource import AudioSource
from speechrecognition import SpeechRecognition, SpeechRecognitionError
from hue import Hue
from config import Config
from logger import Logger

import os
import re

class App():
    def __initLogging(self):
        self.log = Logger.createStaticLogger(
            logfile=os.path.expanduser(self.config.get('log.logfile')),
            loglevel=self.config.get('log.loglevel'),
        )

        self.log.info({
            'msgType': 'Application started',
            'module': self.__class__.__name__,
            'config': self.config.dump(),
        })

    def __initAudioSource(self):
        self.audio = AudioSource(
            audioFile=self.config.get('audio.audio_file'),
            threshold=self.config.get('audio.threshold'),
            chunkSize=self.config.get('audio.chunk_size'),
            rate=self.config.get('audio.rate'))

    def __initSpeechRecognition(self):
        self.speech = SpeechRecognition(
            apiKey=self.config.get('speech.google_speech_api_key'),
            languages=self.config.get('speech.language').split(',')
        )

    def __init__(self):
        self.config = Config()
        self.__initLogging()

        self.__initAudioSource()
        self.audio.recordToFile()

        self.__initSpeechRecognition()

        try:
            text, confidence = self.speech.recognizeSpeechFromFile(filename=self.config.get('audio.audio_file'))
            os.remove(self.config.get('audio.audio_file'))
        except SpeechRecognitionError as e:
            # TODO Properly manage the raised exception with a retry mechanism, see #13
            self.log.warning({
                'msgType': 'Speech not recognized',
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
            hue.setOn(True)

        if (re.search('lights', text.lower(), re.IGNORECASE) and re.search('off', text.lower(), re.IGNORECASE) \
              or \
            re.search('luci', text.lower(), re.IGNORECASE) and re.search('spegn', text.lower(), re.IGNORECASE)):
            hue.connect()
            hue.setOn(False)

if __name__ == '__main__':
    try:
        App()
    except BaseException as e:
        Logger().error({
            'msgType'   : 'Uncaught exception, exiting',
            'exception' : str(e),
        })

        raise e

# vim:sw=4:ts=4:et:

