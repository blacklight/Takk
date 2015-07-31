from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave

class AudioSource():
    # threshold = 500  # audio levels not normalised.
    threshold = 3300  # audio levels not normalised.
    chunkSize = 1024
    silentChunks = 3 * 44100 / 1024  # about 3sec
    format = pyaudio.paInt16
    frameMaxValue = 2 ** 15 - 1
    normalizeMinusOneDb = 10 ** (-1.0 / 20)
    rate = 44100
    channels = 1
    trimAppend = rate / 4

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

    def __isSilent(self, data_chunk):
        """Returns 'True' if below the 'silent' threshold"""
        return max(data_chunk) < self.threshold

    def __normalize(self, data_all):
        """Amplify the volume out to max -1dB"""
        # MAXIMUM = 16384
        normalize_factor = (float(self.normalizeMinusOneDb * self.frameMaxValue)
                            / max(abs(i) for i in data_all))

        r = array('h')
        for i in data_all:
            r.append(int(i * normalize_factor))
        return r

    def __trim(self, data_all):
        _from = 0
        _to = len(data_all) - 1
        for i, b in enumerate(data_all):
            if abs(b) > self.threshold:
                _from = max(0, i - self.trimAppend)
                break

        for i, b in enumerate(reversed(data_all)):
            if abs(b) > self.threshold:
                _to = min(len(data_all) - 1, len(data_all) - 1 - i + self.trimAppend)
                break

        print("FROM: %d" % _from)
        print("TO: %d" % _to)
        return copy.deepcopy(data_all[_from:(_to + 1)])

    def record(self):
        """Record a word or words from the microphone and 
        return the data as an array of signed shorts."""

        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, input=True, output=True, frames_per_buffer=self.chunkSize)

        silentChunks = 0
        audio_started = False
        data_all = array('h')

        while True:
            # little endian, signed short
            data_chunk = array('h', stream.read(self.chunkSize))
            if byteorder == 'big':
                data_chunk.byteswap()
            data_all.extend(data_chunk)

            silent = self.__isSilent(data_chunk)
            print(silent)

            if audio_started:
                if silent:
                    silentChunks += 1
                    if silentChunks > self.silentChunks:
                        print("AUDIO STOPPED")
                        break
                else: 
                    silentChunks = 0
            elif not silent:
                print("AUDIO STARTED")
                audio_started = True              

        sample_width = p.get_sample_size(self.format)
        stream.stop_stream()
        stream.close()
        p.terminate()

        data_all = self.__trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as isSilent() function)
        data_all = self.__normalize(data_all)
        return sample_width, data_all

    def recordToFile(self, path):
        "Records from the microphone and outputs the resulting data to 'path'"
        sample_width, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        wave_file = wave.open(path, 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(self.rate)
        wave_file.writeframes(data)
        wave_file.close()

