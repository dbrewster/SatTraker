import json
from typing import List
from abc import ABC, abstractmethod


class SettingsObserver(ABC):
    @abstractmethod
    def valueChanged(self, param, oldValue, newValue) -> None:
        pass


# noinspection SpellCheckingInspection
class Controller:
    _trackSettings = {
        "windowwidth": 800,
        "windowheight": 600,
        "objectfollow": False,
        "telescopeType": 'ASCOM',
        "comPort": 0,
        "camera": 0,
        "mountType": 'Eq',
        "tracking": False,
        "boxSize": 50,
        "mousecoords": (320, 240),
        "degorhours": 'Degrees',
        "mainviewX": 320,
        "mainviewY": 240,
        "setcenter": False,
        "imageScale": 1.0,
        "orbitFile": '',
        "fileSelected": False,
        "Lat": 0.0,
        "Lon": 0.0,
        "trackingSat": False,
        "trackingtype": 'Features',
        "minbright": 50,
        "clickpixel": 0,
        "maxpixel": 255,
        "flipHorizontal": False,
        "flipVertical": False,
        "foundtarget": False,
        "rotate": 0,
        "calibratestart": False,
        "displayFPS": 10,
        "exposure": -3,
        "gain": 0,
        "refreshRate": 20
    }

    _listeners = {}

    def __init__(self):
        # geolocation = geocoder.ip('me')
        pass

    def addObserver(self, param, observer):
        if param not in self._listeners:
            inner_list: List[SettingsObserver] = []
            self._listeners[param] = inner_list
        else:
            inner_list = self._listeners[param]
            
        inner_list.append(observer)

    def removeObserver(self, param, listener):
        if param in self._listeners:
            self._listeners[param].remove(listener)

    def set(self, param, value):
        old_value = self._trackSettings[param]
        if value != old_value:
            self._trackSettings[param] = value
            if param in self._listeners:
                for observer in self._listeners[param]:
                    observer.valueChanged(param, old_value, value)

    def get(self, param):
        return self._trackSettings[param]

    def readConfig(self):
        try:
            with open("Satconfig.json", "r") as json_file:
                self._trackSettings.update(json.load(json_file))
        except:
            print('Config file not present or corrupted.')

    def writeConfig(self):
        with open("Satconfig.json", "w") as json_file:
            json.dump(self._trackSettings, json_file, indent=4, sort_keys=True)
