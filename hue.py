import re
from phue import Bridge

class Hue():
    def __init__(self, bridge, lightbulb=None):
        self.bridgeAddress = bridge
        self.lightsMap = {}
        self.connected = False

        if lightbulb:
            m = re.split('\s*,\s*', lightbulb)
            self.lightbulbs = m if m else [lightbulb]

    def connect(self):
        if self.connected:
            return

        self.bridge = Bridge(self.bridgeAddress)
        self.bridge.connect()
        self.bridge.get_api()

        for light in self.bridge.lights:
            self.lightsMap[light.name] = light

        if not hasattr(self, 'lightbulbs'):
            self.lightbulbs = []
            for light in self.bridge.lights:
                self.lightbulbs.append(light.name)

        self.connected = True

    def isConnected(self):
        return self.connected

    def setOn(self, on):
        for light in self.lightbulbs:
            self.bridge.set_light(light, 'on', on)
            if on:
                self.bridge.set_light(light, 'bri', 255)

    def setBri(self, bri):
        if bri == 0:
            for light in self.lightbulbs:
                self.bridge.set_light(light, 'on', False)
        else:
            for light in self.lightbulbs:
                if not self.bridge.get_light(light, 'on'):
                    self.bridge.set_light(light, 'on', True)

        self.bridge.set_light(self.lightbulbs, 'bri', bri)

    def setSat(self, sat):
        self.bridge.set_light(self.lightbulbs, 'sat', sat)

    def setHue(self, hue):
        self.bridge.set_light(self.lightbulbs, 'hue', hue)

