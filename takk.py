#!/usr/bin/env python

from __future__ import print_function
from __armando__ import Armando
import json, re, traceback

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

class Takk(object):
    __config = Config.get_config()
    __logger = Logger.get_logger(__name__)

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

        rules = Rules('rules.xml')
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

            pattern_ids = list(map(lambda _: _['id'], patterns))
            matched_rules = rules.get_rules_by_patterns(pattern_ids)

            if len(matched_rules) == 0:
                self.__logger.info({
                    'msg_type': 'No rules associated to the matched patterns',
                    'patterns': json.dumps(patterns),
                })
            else:
                self.__logger.info({
                    'msg_type': 'Rules found',
                    'patterns': json.dumps(patterns),
                    'rules': json.dumps(matched_rules),
                })

                # TODO We only pick up the first rule for now.
                # Eventually we should build a map of all the
                # actions associated to the matched patterns
                # according to the provided rules and establish
                # a priority for executing all of them.
                rule = matched_rules[0]
                actions = rules.get_actions_by_rule(rule)
                for action in actions:
                    rules.run_action(action)

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

