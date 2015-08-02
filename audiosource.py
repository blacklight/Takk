from array import array
from struct import pack
from sys import byteorder

import copy
import os
import re
import pyaudio
import wave

class AudioSource():
    # threshold = 500  # audio levels not normalised.
    threshold = 5000  # audio levels not normalised.
    chunkSize = 32768
    rate = 44100
    silentChunks = int(2 * rate / chunkSize) # about 2 sec
    maxChunks = int(3 * rate / chunkSize) # 3 sec
    format = pyaudio.paInt16
    frameMaxValue = 2 ** 15 - 1
    normalizeMinusOneDb = 10 ** (-1.0 / 20)
    channels = 1
    trimAppend = rate / 4
    silentChunksThreshold = 10

    def init(self, threshold=None, chunkSize=None, silentSeconds=3):
        self.threshold = threshold if threshold is not None else __class__.threshold
        self.chunkSize = chunkSize if chunkSize is not None else __class__.chunkSize
        self.silentSeconds = silentSeconds if silentSeconds is not None else __class__.silentSeconds
        self.format = __class__.format
        self.frameMaxValue = __class__.frameMaxValue
        self.normalizeMinusOneDb = __class__.normalizeMinusOneDb
        self.rate = __class__.rate
        self.channels = __class__.channels
        self.trimAppend = __class__.trimAppend

    def __isSilent(self, dataChunk):
        """Returns 'True' if below the 'silent' threshold"""
        return max(dataChunk) < self.threshold

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

        silentChunks = 0
        audioStarted = False
        dataAll = array('h')

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

        dataAll = self.__trim(dataAll)  # we trim before normalize as threshhold applies to un-normalized wave (as well as isSilent() function)
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

    def recordToFile(self, path):
        "Records from the microphone and outputs the resulting data to 'path'"
        sampleWidth, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        basename, extension = self.__splitFilename(path)
        waveFileName = '%s.wav' % basename
        waveFile = wave.open(waveFileName, 'wb')
        waveFile.setnchannels(self.channels)
        waveFile.setsampwidth(sampleWidth)
        waveFile.setframerate(self.rate)
        waveFile.writeframes(data)
        waveFile.close()

        if extension.lower() == 'flac':
            os.system('flac -f %s -o %s.flac' % (waveFileName, basename))
            os.remove(waveFileName)

