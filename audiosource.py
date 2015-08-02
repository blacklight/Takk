from array import array
from struct import pack
from sys import byteorder
from logger import Logger

import copy
import os
import re
import pyaudio
import wave

class AudioSource():
    """
    @author: Fabio "BlackLight" Manganiello <blacklight86@gmail.com>
    """

    # threshold = 500  # audio levels not normalised.
    threshold = 5000  # audio levels not normalised.
    chunkSize = 32768
    rate = 44100
    maxChunks = int(3 * rate / chunkSize) # 3 sec
    format = pyaudio.paInt16
    frameMaxValue = 2 ** 15 - 1
    normalizeMinusOneDb = 10 ** (-1.0 / 20)
    channels = 1
    trimAppend = rate / 4

    def __init__(self,
             audioFile=None,
             threshold=None,
             chunkSize=None,
             rate=None):
        if audioFile is not None:
            self.audioFile = audioFile
        else:
            raise Exception('No audio.audio_file item specified in your configuration')

        self.threshold = int(threshold) if threshold is not None else __class__.threshold
        self.chunkSize = int(chunkSize) if chunkSize is not None else __class__.chunkSize
        self.rate = int(rate) if rate is not None else __class__.rate
        self.maxChunks = int(3 * self.rate / self.chunkSize)
        self.format = __class__.format
        self.frameMaxValue = __class__.frameMaxValue
        self.normalizeMinusOneDb = __class__.normalizeMinusOneDb
        self.channels = __class__.channels
        self.trimAppend = __class__.trimAppend

        Logger.getLogger().info({
            'msgType': 'Initializing audio source',
            'module': self.__class__.__name__,
            'threshold': self.threshold,
            'chunkSize': self.chunkSize,
            'rate': self.rate,
            'channels': self.channels,
            'frameMaxValue': self.frameMaxValue,
        })

    def __normalize(self, dataAll):
        """Amplify the volume out to max -1dB"""
        # MAXIMUM = 16384
        normalizeFactor = (float(self.normalizeMinusOneDb * self.frameMaxValue)
                            / max(abs(i) for i in dataAll))

        r = array('h')
        for i in dataAll:
            r.append(int(i * normalizeFactor))
        return r

    def __trim(self, dataAll):
        _from = 0
        _to = len(dataAll) - 1
        for i, b in enumerate(dataAll):
            if abs(b) > self.threshold:
                _from = int(max(0, i - self.trimAppend))
                break

        for i, b in enumerate(reversed(dataAll)):
            if abs(b) > self.threshold:
                _to = int(min(len(dataAll) - 1, len(dataAll) - 1 - i + self.trimAppend))
                break

        return copy.deepcopy(dataAll[_from:(_to + 1)])

    def record(self):
        """Record a word or words from the microphone and 
        return the data as an array of signed shorts."""

        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, output=True, frames_per_buffer=self.chunkSize)

        audioStarted = False
        dataAll = array('h')

        Logger.getLogger().info({
            'msgType': 'Audio recording started',
            'module': self.__class__.__name__
        })

        while int(len(dataAll) / self.chunkSize) < self.maxChunks:
            # little endian, signed short
            dataChunk = array('h', stream.read(self.chunkSize))
            if byteorder == 'big':
                dataChunk.byteswap()
            dataAll.extend(dataChunk)

        sampleWidth = p.get_sample_size(self.format)
        stream.stop_stream()
        stream.close()
        p.terminate()

        Logger.getLogger().info({
            'msgType': 'Audio recording stopped',
            'module': self.__class__.__name__
        })

        dataAll = self.__trim(dataAll)
        dataAll = self.__normalize(dataAll)
        return sampleWidth, dataAll

    @staticmethod
    def __splitFilename(filename):
        basename = filename
        extension = 'wav'
        m = re.match('(.*)\.(.*)', filename)
        if m:
            basename = m.group(1)
            extension = m.group(2).lower()

        return basename, extension

    def recordToFile(self):
        "Records from the microphone and outputs the resulting data to the file"
        sampleWidth, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        basename, extension = self.__splitFilename(self.audioFile)
        waveFileName = '%s.wav' % basename
        waveFile = wave.open(waveFileName, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(sampleWidth)
        waveFile.setframerate(self.rate)
        waveFile.writeframes(data)
        waveFile.close()

        Logger.getLogger().debug({
            'msgType': 'Saved recorded audio to wave file',
            'module': self.__class__.__name__,
            'filename': waveFileName,
        })

        if extension.lower() == 'flac':
            flacFileName = '%s.flac' % basename
            os.system('flac -f %s -o %s > /dev/null 2>&1' % (waveFileName, flacFileName))
            os.remove(waveFileName)

            Logger.getLogger().debug({
                'msgType': 'Saved recorded audio to flac file',
                'module': self.__class__.__name__,
                'filename': waveFileName,
            })

# vim:sw=4:ts=4:et:

