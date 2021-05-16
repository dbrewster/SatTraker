import json

import serial
import win32com.client


# noinspection SpellCheckingInspection
class Controller:
    trackSettings = {
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
        "flip": 'NoFlip',
        "foundtarget": False,
        "rotate": 0,
        "calibratestart": False,
    }

    def __init__(self):
        # geolocation = geocoder.ip('me')

        # LX200 specific variables
        self.ser = None
        self.serialconnected = False

        # Ascom specific vars
        self.x = None
        self.tel = None
        self.axis0rate = 0.0
        self.axis1rate = 0.0

    def readConfig(self):
        try:
            with open("Satconfig.json", "r") as json_file:
                self.trackSettings = json.load(json_file)
        except:
            print('Config file not present or corrupted.')

    def writeConfig(self):
        with open("Satconfig.json", "w") as json_file:
            json.dump(self.trackSettings, json_file, indent=4, sort_keys=True)

    # noinspection PyUnresolvedReferences
    def connectMount(self):
        if self.trackSettings["telescopeType"] == 'LX200':
            com_port = str('COM' + str(self.trackSettings["comPort"]))
            try:
                self.ser = serial.Serial(com_port, baudrate=9600, timeout=1, bytesize=serial.EIGHTBITS,
                                         parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False,
                                         rtscts=False)
                self.ser.write(str.encode(':U#'))
                self.serialconnected = True
                return True, ""
            except:
                print('Failed to connect on ' + com_port)
                return False, 'Failed to connect on ' + str(com_port)
        elif self.trackSettings["telescopeType"] == 'ASCOM':
            self.x = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
            self.x.DeviceType = 'Telescope'
            driver_name = self.x.Choose("None")
            self.tel = win32com.client.Dispatch(driver_name)
            if self.tel.Connected:
                return True, "Telescope was already connected"
            else:
                self.tel.Connected = True
                if self.tel.Connected:
                    axis = self.tel.CanMoveAxis(0)
                    axis2 = self.tel.CanMoveAxis(1)
                    if axis is False or axis2 is False:
                        self.tel.Connected = False
                        return False, 'This scope cannot use the MoveAxis method, aborting.'
                    else:
                        self.axis0rate = float(self.tel.AxisRates(0).Item(1).Maximum)
                        self.axis1rate = float(self.tel.AxisRates(1).Item(1).Maximum)
                        return True, 'Axis 0 max rate: ' + str(self.axis0rate) + ' Axis 1 max rate: ' + \
                            str(self.axis1rate)
                else:
                    return False, "Unable to connect to telescope, expect exception"

    def disconnectMount(self):
        if self.trackSettings["telescopeType"] == 'LX200' and self.serialconnected is True:
            self.ser.write(str.encode(':Q#'))
            self.ser.write(str.encode(':U#'))
            self.ser.close()
            self.serialconnected = False
        elif self.trackSettings["telescopeType"] == 'ASCOM':
            self.tel.AbortSlew()
            self.tel.Connected = False
