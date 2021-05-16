import json
import sys
from tkinter import *
from tkinter import filedialog

import cv2
import geocoder
import numpy as np
import serial
import win32com.client
from PIL import Image as PILImage, ImageTk

import ImageCapture


def blankImage(width, height):
    blank_image = np.zeros((height, width, 3), np.uint8)
    local_tkimg = PILImage.fromarray(blank_image)
    local_tkimg = ImageTk.PhotoImage(image=local_tkimg)
    return local_tkimg


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


# noinspection SpellCheckingInspection
class Controller:
    def __init__(self):
        geolocation = geocoder.ip('me')

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
                global trackSettings
                trackSettings = json.load(json_file)
        except:
            print('Config file not present or corrupted.')

    def writeConfig(self):
        with open("Satconfig.json", "w") as json_file:
            json.dump(trackSettings, json_file, indent=4, sort_keys=True)

    def connectMount(self):
        if trackSettings["telescopeType"] == 'LX200':
            com_port = str('COM' + str(trackSettings["comPort"]))
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
        elif trackSettings["telescopeType"] == 'ASCOM':
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
        if trackSettings["telescopeType"] == 'LX200' and self.serialconnected is True:
            self.ser.write(str.encode(':Q#'))
            self.ser.write(str.encode(':U#'))
            self.ser.close()
            self.serialconnected = False
        elif trackSettings["telescopeType"] == 'ASCOM':
            self.tel.AbortSlew()
            self.tel.Connected = False


def varGetOrDefault(var, default):
    try:
        return var.get()
    except:
        return default


# noinspection PyPep8Naming,PyMethodMayBeStatic,SpellCheckingInspection
class Buttons:
    def __init__(self, master):
        self.controller = Controller()
        self.controller.readConfig()
        self.imageCapture = None
        self.master = master
        master.protocol("WM_DELETE_WINDOW", self.onClose)

        master.geometry(str(trackSettings["windowwidth"]) + "x" + str(trackSettings["windowheight"]))

        master.bind("<Configure>", self.setWindowSize)

        self.collect_images = False
        self.topframe = Frame(master, borderwidth=1, background="blue")
        master.winfo_toplevel().title("SatTraker")
        self.topframe.pack(side=TOP, fill="both", expand=True)
        self.displayimg = Label(self.topframe, highlightthickness=0, bd=0)
        self.displayimg.pack(side=TOP, fill="both", expand=True)

        self.textframe = Frame(master)
        self.textframe.pack(side=BOTTOM)
        self.bottomframe = Frame(master)
        self.bottomframe.pack(side=BOTTOM)
        self.menu = Menu(master)
        master.config(menu=self.menu)

        master.bind("<Up>", self.goup)
        master.bind("<Left>", self.goleft)
        master.bind("<Down>", self.godown)
        master.bind("<Right>", self.goright)

        self.labelLat = Label(self.bottomframe, text='Latitude (N+)')
        self.labelLat.grid(row=5, column=0)
        self.latVal = DoubleVar()
        self.latVal.set(trackSettings["Lat"])
        self.entryLat = Entry(self.bottomframe, textvariable=self.latVal)
        self.entryLat.grid(row=5, column=1)
        self.labelLon = Label(self.bottomframe, text='Longitude (E+)')
        self.labelLon.grid(row=6, column=0)
        self.lonVal = DoubleVar()
        self.lonVal.set(trackSettings["Lon"])
        self.entryLon = Entry(self.bottomframe, textvariable=self.lonVal)
        self.entryLon.grid(row=6, column=1)

        self.latVal.trace("w", self.setLat)
        self.lonVal.trace("w", self.setLon)

        # self.labelBright = Label(self.bottomframe, text='Minimum Brightness')
        # self.labelBright.grid(row=8, column = 0)
        # self.entryBright = Entry(self.bottomframe)
        # self.entryBright.grid(row = 8, column = 1)

        # self.entryBright.insert(0, trackSettings["minbright"])
        self.startButton = Button(self.bottomframe, text='Start Camera', command=self.set_img_collect)
        self.startButton.grid(row=1, column=0)
        self.startButton2 = Button(self.bottomframe, text='Camera Calibration', command=self.start_calibration)
        self.startButton2.grid(row=4, column=0)
        self.startButton3 = Button(self.bottomframe, text='Set Center Point', command=self.set_center)
        self.startButton3.grid(row=4, column=1)
        self.startButton4 = Button(self.bottomframe, text='Start Tracking Satellite', command=self.start_sat_track)
        self.startButton4.grid(row=7, column=1)
        self.startButton5 = Button(self.bottomframe, text='Connect Scope', command=self.toggleMountTracking)
        self.startButton5.grid(row=1, column=1)
        self.ComLabel = Label(self.bottomframe, text='COM Port')
        self.ComLabel.grid(row=2, column=0)
        self.comNumber = IntVar()
        self.entryCom = Entry(self.bottomframe, textvariable=self.comNumber)
        self.entryCom.grid(row=2, column=1)
        self.textbox = Text(self.textframe, height=4, width=100)
        self.textbox.grid(row=1, column=0)
        self.comNumber.set(trackSettings["comPort"])
        self.comNumber.trace("w", self.setComPort)

        self.CameraLabel = Label(self.bottomframe, text='Camera Number')
        self.CameraLabel.grid(row=3, column=0)
        self.camNumber = IntVar()
        self.entryCam = Entry(self.bottomframe, textvariable=self.camNumber)
        self.entryCam.grid(row=3, column=1)
        self.camNumber.set(trackSettings["camera"])
        self.camNumber.trace("w", self.setCamera)

        self.fileMenu = Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.fileMenu)
        self.fileMenu.add_command(label='Select TLE File...', command=self.filePicker)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label='Exit and Save Configuration', command=self.exitProg)

        self.telescopeMenu = Menu(self.menu)
        self.menu.add_cascade(label='Telescope Type', menu=self.telescopeMenu)
        self.telescopeMenu.add_command(label='LX200 Classic Alt/Az', command=self.setLX200AltAz)
        self.telescopeMenu.add_command(label='LX200 Classic Equatorial', command=self.setLX200Eq)
        self.telescopeMenu.add_command(label='ASCOM Alt/Az', command=self.setASCOMAltAz)
        self.telescopeMenu.add_command(label='ASCOM Equatorial', command=self.setASCOMEq)

        self.trackingMenu = Menu(self.menu)
        self.menu.add_cascade(label='Tracking Type', menu=self.trackingMenu)
        self.trackingMenu.add_command(label='Feature Tracking', command=self.setFeatureTrack)
        self.trackingMenu.add_command(label='Brightness Tracking', command=self.setBrightTrack)

        self.imageMenu = Menu(self.menu)
        self.menu.add_cascade(label='Image Orientation', menu=self.imageMenu)
        self.imageMenu.add_command(label='Normal Orientation', command=self.setNoFlip)
        self.imageMenu.add_command(label='Vertical Flip', command=self.setVerticalFlip)
        self.imageMenu.add_command(label='Horizontal Flip', command=self.setHorizontalFlip)
        self.imageMenu.add_command(label='Vertical and Horizontal Flip', command=self.setVerticalHorizontalFlip)
        self.imageMenu.add_command(label='Rotate Image 0 Degrees', command=self.set0Rotate)
        self.imageMenu.add_command(label='Rotate Image 90 Degrees', command=self.setPos90Rotate)
        self.imageMenu.add_command(label='Rotate Image -90 Degrees', command=self.setNeg90Rotate)
        self.imageMenu.add_command(label='Rotate Image 180 Degrees', command=self.set180Rotate)

    def onClose(self):
        self.controller.writeConfig()
        self.master.destroy()

    # noinspection PyUnusedLocal
    def setWindowSize(self, *args):
        trackSettings["windowwidth"] = self.master.winfo_width()
        trackSettings["windowheight"] = self.master.winfo_height()

    # noinspection PyUnusedLocal
    def setLat(self, *args):
        trackSettings["Lat"] = varGetOrDefault(self.latVal, 0.0)

    # noinspection PyUnusedLocal
    def setLon(self, *args):
        trackSettings["Lon"] = varGetOrDefault(self.lonVal, 0.0)

    # noinspection PyUnusedLocal
    def setComPort(self, *args):
        trackSettings["comPort"] = varGetOrDefault(self.comNumber, 0)

    # noinspection PyUnusedLocal
    def setCamera(self, *args):
        trackSettings["camera"] = varGetOrDefault(self.camNumber, 0)

    def setNoFlip(self):
        trackSettings["flip"] = 'NoFlip'

    def setVerticalFlip(self):
        trackSettings["flip"] = 'VerticalFlip'

    def setHorizontalFlip(self):
        trackSettings["flip"] = 'HorizontalFlip'

    def setVerticalHorizontalFlip(self):
        trackSettings["flip"] = 'VerticalHorizontalFlip'

    def set0Rotate(self):
        trackSettings["rotate"] = 0

    def setPos90Rotate(self):
        trackSettings["rotate"] = 90

    def setNeg90Rotate(self):
        trackSettings["rotate"] = -90

    def set180Rotate(self):
        trackSettings["rotate"] = 180

    def exitProg(self):
        if self.collect_images:
            self.set_img_collect()
        self.controller.writeConfig()
        sys.exit()

    def filePicker(self):
        trackSettings["orbitFile"] = filedialog.askopenfilename(initialdir=".", title="Select TLE file", filetypes=(
            ("text files", "*.txt"), ("tle files", "*.tle"), ("all files", "*.*")))
        trackSettings["fileSelected"] = True
        print(trackSettings["orbitFile"])
        self.textbox.insert(END, str(str(trackSettings["orbitFile"]) + '\n'))
        self.textbox.see('end')

    def set_center(self):
        trackSettings["setcenter"] = True

    def setLX200AltAz(self):
        trackSettings["telescopeType"] = 'LX200'
        trackSettings["mountType"] = 'AltAz'

    def setLX200Eq(self):
        trackSettings["telescopeType"] = 'LX200'
        trackSettings["mountType"] = 'Eq'

    def setFeatureTrack(self):
        trackSettings["trackingtype"] = 'Features'

    def setBrightTrack(self):
        trackSettings["trackingtype"] = 'Bright'

    def setASCOMAltAz(self):
        trackSettings["telescopeType"] = 'ASCOM'
        trackSettings["mountType"] = 'AltAz'

    def setASCOMEq(self):
        trackSettings["telescopeType"] = 'ASCOM'
        trackSettings["mountType"] = 'Eq'

    def toggleMountTracking(self):
        if trackSettings["tracking"] is False:
            trackSettings["tracking"] = True
            print('Connecting to Scope.')
            self.textbox.insert(END, 'Connecting to Scope.\n')
            self.textbox.see('end')
            status, msg = self.controller.connectMount()
            if status:
                self.startButton5.configure(text='Disconnect Scope')
            else:
                trackSettings["tracking"] = False
            if msg:
                print(msg)
                self.textbox.insert(END, str(msg + '\n'))
                self.textbox.see('end')

        else:
            print('Disconnecting the Scope.')
            self.textbox.insert(END, str('Disconnecting the scope.\n'))
            self.textbox.see('end')
            self.controller.disconnectMount()
            trackSettings["tracking"] = False
            self.startButton5.configure(text='Connect Scope')

    # noinspection PyUnusedLocal
    def goup(self, event):
        trackSettings["mainviewY"] -= 1
        self.imageCapture.incExposure()

    # noinspection PyUnusedLocal
    def godown(self, event):
        trackSettings["mainviewY"] += 1
        self.imageCapture.decExposure()

    # noinspection PyUnusedLocal
    def goleft(self, event):
        trackSettings["mainviewX"] -= 1

    # noinspection PyUnusedLocal
    def goright(self, event):
        trackSettings["mainviewX"] += 1

    def start_sat_track(self):
        pass

    def sat_track(self):
        pass

    def start_calibration(self):
        pass

    def set_img_collect(self):
        if self.collect_images:
            self.startButton.configure(text='Start Camera')
            self.imageCapture.stopCapture()
            self.collect_images = False
        else:
            options = ImageCapture.ImageOptions()
            options.cameraNum = self.camNumber.get()
            self.startButton.configure(text='Stop Camera')
            self.imageCapture = ImageCapture.ImageCapture(options)
            self.imageCapture.addObserver(ImageRenderer(self.displayimg, self.topframe))
            self.imageCapture.startCaputure()
            self.collect_images = True


class ImageRenderer(ImageCapture.ImageObserver):
    def __init__(self, imageElement, parent) -> None:
        super().__init__()
        self.imageElement = imageElement
        self.lastUpdate = 0
        self.framesCaptured = 0
        self.parent = parent

    def processingStarted(self) -> None:
        pass

    def imageCaptured(self, img: ImageCapture.Image) -> None:
        local_img = img.img
        e_width = self.parent.winfo_width() - 2
        e_height = self.parent.winfo_height() - 2
        height, width, channels = local_img.shape
        if width != e_width or height != e_height:
            scale = min(e_width / width, e_height / height)
            dsize = (int(width * scale), int(height * scale))
            local_img = cv2.resize(local_img, dsize)
        local_b, local_g, local_r = cv2.split(local_img)
        local_tkimg = cv2.merge((local_r, local_g, local_b))
        local_tkimg = PILImage.fromarray(local_tkimg)
        local_tkimg = ImageTk.PhotoImage(image=local_tkimg)
        self.imageElement.config(image=local_tkimg)
        self.imageElement.img = local_tkimg
        self.imageElement.grid(row=0, column=0)
        self.framesCaptured += 1
        if img.captureTime - self.lastUpdate > 1:
            print("frames per sec = " + str(self.framesCaptured / (img.captureTime - self.lastUpdate)))
            self.framesCaptured = 0
            self.lastUpdate = img.captureTime

    def processingDone(self) -> None:
        self.imageElement.config(image="")
        self.imageElement.pack(side=TOP, fill="both", expand=True)


root = Tk()
b = Buttons(root)
root.mainloop()
