#!/usr/bin/env python

from __future__ import print_function

from audiosource import AudioSource
from speechrecognition import SpeechRecognition, SpeechRecognitionError
from hue import Hue
from config import Config
from logger import Logger

import os
import re

def main():
    config = Config()
    log = Logger.createStaticLogger(logfile=os.path.expanduser(config.get('log.logfile')))
    log.info({
        'msgType': 'Application started',
        'module': __name__,
        'config': config.dump(),
    })

    hue = Hue(bridge=config.get('hue.bridge'))

    source = AudioSource(
        audioFile=config.get('audio.audio_file'),
        threshold=config.get('audio.threshold'),
        chunkSize=config.get('audio.chunk_size'),
        rate=config.get('audio.rate'))

    speech = SpeechRecognition(
        apiKey=config.get('speech.google_speech_api_key'),
        languages=config.get('speech.language').split(',')
    )

    source.recordToFile()

    try:
        text, confidence = speech.recognizeSpeechFromFile(filename=config.get('audio.audio_file'))
    except SpeechRecognitionError as e:
        log.warning({
            'msgType': 'Speech not recognized',
            'module': __name__,
        })

        raise e

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
        main()
    except BaseException as e:
        Logger().error({
            'msgType'   : 'Uncaught exception, exiting',
            'exception' : str(e),
        })

        raise e

# vim:sw=4:ts=4:et:

