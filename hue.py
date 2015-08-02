import re

from logger import Logger
from phue import Bridge

class Hue():
    __moduleName = 'hue'

    def __init__(self, bridge, lightbulb=None):
        self.bridgeAddress = bridge
        self.lightsMap = {}
        self.connected = False

        if lightbulb:
            m = re.split('\s*,\s*', lightbulb)
            self.lightbulbs = m if m else [lightbulb]

        Logger.getLogger().info({
            'msgType': 'Hue bridge started',
            'bridge': self.bridgeAddress,
            'module': self.__moduleName,
            'lightbulbs': self.lightbulbs if lightbulb else None,
        })

    def connect(self):
        if self.connected:
            return

        Logger.getLogger().info({
            'msgType': 'Connecting to the Hue bridge',
            'module': self.__moduleName,
        })

        self.bridge = Bridge(self.bridgeAddress)
        self.bridge.connect()
        self.bridge.get_api()

        Logger.getLogger().info({
            'msgType': 'Connected to the Hue bridge',
            'module': self.__moduleName,
        })

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
        Logger.getLogger().info({
            'msgType': 'Set lightbulbs on',
            'module': self.__moduleName,
            'on': on,
        })

        for light in self.lightbulbs:
            self.bridge.set_light(light, 'on', on)
            if on:
                self.bridge.set_light(light, 'bri', 255)

    def setBri(self, bri):
        Logger.getLogger().info({
            'msgType': 'Set lightbulbs brightness',
            'module': self.__moduleName,
            'brightness': bri,
        })

        if bri == 0:
            for light in self.lightbulbs:
                self.bridge.set_light(light, 'on', False)
        else:
            for light in self.lightbulbs:
                if not self.bridge.get_light(light, 'on'):
                    self.bridge.set_light(light, 'on', True)

        self.bridge.set_light(self.lightbulbs, 'bri', bri)

    def setSat(self, sat):
        Logger.getLogger().info({
            'msgType': 'Set lightbulbs saturation',
            'module': self.__moduleName,
            'saturation': sat,
        })

        self.bridge.set_light(self.lightbulbs, 'sat', sat)

    def setHue(self, hue):
        Logger.getLogger().info({
            'msgType': 'Set lightbulbs hue',
            'module': self.__moduleName,
            'saturation': hue,
        })

        self.bridge.set_light(self.lightbulbs, 'hue', hue)

