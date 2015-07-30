#!/usr/bin/python2

from __future__ import print_function

import speech_recognition as sr
import time

def onVoiceSample(recognizer, audio):
    try:
        phrase = recognizer.recognize(audio)
        print('You said "%s"' % phrase)
    except LookupError as e:
        print('Could not understand you: %s' % e)

recognizer = sr.Recognizer()
microphone = sr.Microphone()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)

stop_listening = recognizer.listen_in_background(microphone, onVoiceSample)

for _ in range(50):
    time.sleep(0.1)

stop_listening()

while True:
    time.sleep(0.1)

