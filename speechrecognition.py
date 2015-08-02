from __future__ import print_function
from logger import Logger

import json
import os
import re
import requests

try:
    from urllib.parse import urlencode
except ImportError as e:
    from urllib import urlencode

class SpeechRecognitionError(Exception):
    pass

class SpeechRecognition():
    """
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    def __init__(self, apiKey=None, languages=['en-us']):
        if not apiKey:
            raise Exception('No Google speech recognition API key found in your configuration or GOOGLE_SPEECH_API_KEY environment variable')

        self.apiKey = apiKey
        self.languages = languages

        Logger.getLogger().info({
            'msgType': 'Initializing speech recognition backend',
            'module': self.__class__.__name__,
            'apiKey': '******',
            'languages': languages,
        })

    def recognizeSpeechFromFile(self, filename):
        Logger.getLogger().info({
            'msgType': 'Google Speech Recognition API request',
            'module': self.__class__.__name__,
            'apiKey': '******',
            'language': self.languages[0],
        })

        r = requests.post( \
            'http://www.google.com/speech-api/v2/recognize?' + urlencode({
                'lang': self.languages[0],
                'key': self.apiKey,
                'output': 'json',
            }),

            data = open(filename, 'rb').read(),
            headers = {
                'Content-type': 'audio/x-flac; rate=44100',
            },
        )

        if not r.ok:
            raise Exception('Got an unexpected HTTP response %d from the server' % r.status_code)

        Logger.getLogger().info({
            'msgType': 'Google Speech Recognition API response',
            'module': self.__class__.__name__,
            'response': r.text,
        })

        response = []
        for line in re.split('\r?\n', r.text):
            if re.match('^\s*$', line):
                continue
            response.append(json.loads(line))

        for item in response:
            if 'result' in item and len(item['result']):
                for _ in item['result']:
                    if 'final' in _:
                        if 'alternative' in _ and len(_['alternative']):
                            return _['alternative'][0]['transcript'], \
                                _['alternative'][0]['confidence'] if 'confidence' in _['alternative'][0] else 1

        raise SpeechRecognitionError('Speech not recognized')

# vim:sw=4:ts=4:et:

