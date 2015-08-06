# Takk

# ** IMPORTANT: TAKK IS PART OF THE ARMANDO PLATFORM https://github.com/BlackLight/Armando **
# ** THEREFORE USE IT BY CLONING THE ARMANDO PLATFORM GIT PROJECT **

Takk is more or less a Python and Unix-friendly version of Google Now, Siri or Cortana. It allows you to create custom speech-based commands on your Unix box, relying on the Google Speech Recognition API.

## Requirements

* `flac` executable (check your OS distribution on how to install it - e.g. `apt-get install flac` on Debian/Ubuntu or `pacman -S flac` on Arch Linux), in order to convert raw WAV recording in the FLAC format used by Google Speech Recognition API.

* `pyaudio` (e.g. `pip install pyaudio`).

* `requests` module (e.g. `pip install requests`), used to make HTTP requests to the Google Speech backend.

* `phue` in case you want to use Takk together with Philips Hue lightbulbs.

## Installation

1. `git clone https://github.com/BlackLight/Armando.git`
2. `cd Armando`
3. `git submodule init`
4. `git submodule update`
5. `cd share/Takk`
6. Modify `./takkrc` to include your Google Speech Recognition API secret key. Instructions on how to get one: http://www.chromium.org/developers/how-tos/api-keys
7. Customize `./takkrc` according to the provided in-file documentation
8. `./takk.py`

