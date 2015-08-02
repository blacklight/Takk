import json
import os
import re
import requests

from sys import version_info
PY3 = version_info[0] >= 3

if PY3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

class SpeechRecognition():
    apiKey = 'AIzaSyB_Gv4eluclBegc7OdRB4pk5LYPfuQCTBo'

    def __init__(self):
        pass

    def recognizeSpeechFromFile(self, filename, language='en-us'):
        r = requests.post( \
            'http://www.google.com/speech-api/v2/recognize?' + urlencode({
                'lang': language,
                'key': __class__.apiKey,
                'output': 'json',
            }),

            data = open(filename, 'rb').read(),
            headers = {
                'Content-type': 'audio/x-flac; rate=44100',
            },
        )

        if not r.ok:
            raise Exception('Got an unexpected HTTP response %d from the server' % r.status_code)

        response = []
        for line in re.split('\r?\n', r.text):
            if re.match('^\s*$', line):
                continue
            response.append(json.loads(line))

        for item in response:
            print(item)
            if 'result' in item and len(item['result']):
                for _ in item['result']:
                    if 'final' in _:
                        if 'alternative' in _ and len(_['alternative']):
                            return _['alternative'][0]['transcript'], \
                                _['alternative'][0]['confidence'] if 'confidence' in _['alternative'][0] else 1

