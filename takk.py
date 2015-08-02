#!/usr/bin/env python

from __future__ import print_function
from audiosource import AudioSource
from speechrecognition import SpeechRecognition
from hue import Hue
from config import Config

import os
import re

def main():
    config = Config()

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
    text, confidence = speech.recognizeSpeechFromFile(filename=config.get('audio.audio_file'))

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
    main()

