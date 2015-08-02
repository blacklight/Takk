#!/usr/bin/env python

from audiosource import AudioSource
from speechrecognition import SpeechRecognition
from hue import Hue

import os
import re

config = {
    'audiofile': 'audio.flac',
    'huebridge': 'hue',
    'lang': 'en-us',
}

def main():
    global config

    hue = Hue(config['huebridge'])
    AudioSource().recordToFile(config['audiofile'])
    text, confidence = SpeechRecognition().recognizeSpeechFromFile(filename=config['audiofile'], language=config['lang'])

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

