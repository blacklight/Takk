#!/usr/bin/python

from audiosource import AudioSource

def main():
    print("Wait in silence to begin recording; wait in silence to terminate")
    source = AudioSource()
    source.recordToFile('demo.wav')
    print("done - result written to demo.wav")

if __name__ == '__main__':
    main()

