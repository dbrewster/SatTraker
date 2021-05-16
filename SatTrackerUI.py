from tkinter import *
from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image as PILImage, ImageTk

import ImageCapture
from Controller import Controller


def blankImage(width, height):
    blank_image = np.zeros((height, width, 3), np.uint8)
    local_tkimg = PILImage.fromarray(blank_image)
    local_tkimg = ImageTk.PhotoImage(image=local_tkimg)
    return local_tkimg


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

        master.winfo_toplevel().title("SatTraker")
        master.protocol("WM_DELETE_WINDOW", self.onClose)

        master.geometry(str(self.controller.trackSettings["windowwidth"]) + "x" + str(self.controller.trackSettings["windowheight"]))

        master.bind("<Configure>", self.setWindowSize)

        self.buttonFrame = Frame(master, height=32, bg="black")
        self.buttonFrame.pack(side=TOP, fill="x")
        self.buttonFrame.grid_propagate(False)

        startCamera = PILImage.open("./start_camera.png").resize((30, 30))
        self.startCameraButton = ImageTk.PhotoImage(startCamera)
        stopCamera = PILImage.open("./stop_camera.png").resize((30, 30))
        self.stopCameraButton = ImageTk.PhotoImage(stopCamera)
        self.startButton = Button(self.buttonFrame, image=self.startCameraButton, command=self.set_img_collect, highlightthickness=0, bd=0)
        self.startButton.pack(anchor="e", padx=4, pady=4)

        settingsFrame = Frame(master, width="24", background="white")
        settingsFrame.pack(side=RIGHT, fill="y")

        self.showSettingsImage = ImageTk.PhotoImage(PILImage.open("./settings.png").resize((22, 22)))
        showSettingsBtn = Button(settingsFrame, image=self.showSettingsImage, command=self.popWindow, background="white", bd=0)
        showSettingsBtn.pack(pady=14)

        self.collect_images = False
        self.cameraFrame = Frame(master, borderwidth=1, background="white")
        self.cameraFrame.pack(side=TOP, fill="both", expand=True)

        self.displayimg = Label(self.cameraFrame, highlightthickness=0, bd=0)
        self.displayimg.pack(side=TOP, fill="both", expand=True)

        self.menu = Menu(master)
        master.config(menu=self.menu)

        master.bind("<Up>", self.goup)
        master.bind("<Left>", self.goleft)
        master.bind("<Down>", self.godown)
        master.bind("<Right>", self.goright)

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

    def popWindow(self):
        SettingsPopup(self.master, self.controller)

    def onClose(self):
        self.controller.writeConfig()
        self.master.destroy()

    # noinspection PyUnusedLocal
    def setWindowSize(self, *args):
        self.controller.trackSettings["windowwidth"] = self.master.winfo_width()
        self.controller.trackSettings["windowheight"] = self.master.winfo_height()

    def setNoFlip(self):
        self.controller.trackSettings["flip"] = 'NoFlip'

    def setVerticalFlip(self):
        self.controller.trackSettings["flip"] = 'VerticalFlip'

    def setHorizontalFlip(self):
        self.controller.trackSettings["flip"] = 'HorizontalFlip'

    def setVerticalHorizontalFlip(self):
        self.controller.trackSettings["flip"] = 'VerticalHorizontalFlip'

    def set0Rotate(self):
        self.controller.trackSettings["rotate"] = 0

    def setPos90Rotate(self):
        self.controller.trackSettings["rotate"] = 90

    def setNeg90Rotate(self):
        self.controller.trackSettings["rotate"] = -90

    def set180Rotate(self):
        self.controller.trackSettings["rotate"] = 180

    def exitProg(self):
        if self.collect_images:
            self.set_img_collect()
        self.controller.writeConfig()
        sys.exit()

    def filePicker(self):
        self.controller.trackSettings["orbitFile"] = filedialog.askopenfilename(initialdir=".", title="Select TLE file", filetypes=(
            ("text files", "*.txt"), ("tle files", "*.tle"), ("all files", "*.*")))
        self.controller.trackSettings["fileSelected"] = True
        print(self.controller.trackSettings["orbitFile"])

    def set_center(self):
        self.controller.trackSettings["setcenter"] = True

    def setLX200AltAz(self):
        self.controller.trackSettings["telescopeType"] = 'LX200'
        self.controller.trackSettings["mountType"] = 'AltAz'

    def setLX200Eq(self):
        self.controller.trackSettings["telescopeType"] = 'LX200'
        self.controller.trackSettings["mountType"] = 'Eq'

    def setFeatureTrack(self):
        self.controller.trackSettings["trackingtype"] = 'Features'

    def setBrightTrack(self):
        self.controller.trackSettings["trackingtype"] = 'Bright'

    def setASCOMAltAz(self):
        self.controller.trackSettings["telescopeType"] = 'ASCOM'
        self.controller.trackSettings["mountType"] = 'AltAz'

    def setASCOMEq(self):
        self.controller.trackSettings["telescopeType"] = 'ASCOM'
        self.controller.trackSettings["mountType"] = 'Eq'

    def toggleMountTracking(self):
        if self.controller.trackSettings["tracking"] is False:
            self.controller.trackSettings["tracking"] = True
            print('Connecting to Scope.')
            self.textbox.insert(END, 'Connecting to Scope.\n')
            self.textbox.see('end')
            status, msg = self.controller.connectMount()
            if status:
                self.startButton5.configure(text='Disconnect Scope')
            else:
                self.controller.trackSettings["tracking"] = False
            if msg:
                print(msg)
                self.textbox.insert(END, str(msg + '\n'))
                self.textbox.see('end')

        else:
            print('Disconnecting the Scope.')
            self.textbox.insert(END, str('Disconnecting the scope.\n'))
            self.textbox.see('end')
            self.controller.disconnectMount()
            self.controller.trackSettings["tracking"] = False
            self.startButton5.configure(text='Connect Scope')

    # noinspection PyUnusedLocal
    def goup(self, event):
        self.controller.trackSettings["mainviewY"] -= 1
        self.imageCapture.incExposure()

    # noinspection PyUnusedLocal
    def godown(self, event):
        self.controller.trackSettings["mainviewY"] += 1
        self.imageCapture.decExposure()

    # noinspection PyUnusedLocal
    def goleft(self, event):
        self.controller.trackSettings["mainviewX"] -= 1

    # noinspection PyUnusedLocal
    def goright(self, event):
        self.controller.trackSettings["mainviewX"] += 1

    def start_sat_track(self):
        pass

    def sat_track(self):
        pass

    def start_calibration(self):
        pass

    def set_img_collect(self):
        if self.collect_images:
            self.startButton.configure(image=self.startCameraButton)
            self.imageCapture.stopCapture()
            self.collect_images = False
        else:
            options = ImageCapture.ImageOptions()
            options.cameraNum = self.controller.trackSettings["camera"]
            self.startButton.configure(image=self.stopCameraButton)
            self.imageCapture = ImageCapture.ImageCapture(options)
            self.imageCapture.addObserver(ImageRenderer(self.displayimg, self.cameraFrame, self.controller.trackSettings["displayFPS"]))
            self.imageCapture.startCaputure()
            self.collect_images = True


class SettingsPopup(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, background="#bbb", bd=1)
        self.controller = controller
        self.place(anchor="ne", relx=1, y=50)
        # self.geometry(str(400) + "x" + str(400))

        whiteframe = Frame(self)
        whiteframe.pack(fill="both", expand=2, padx=1, pady=1)

        self.closeBtn = ImageTk.PhotoImage(PILImage.open("./close_btn.png").resize((8, 8)))
        buttonClose = Button(whiteframe, image=self.closeBtn, command=self.closeSettings)
        buttonClose.pack(anchor="w")
        # buttonClose.place(anchor="nw")

        bottomframe1 = Frame(whiteframe)
        bottomframe1.pack(side=BOTTOM)

        CameraLabel = Label(bottomframe1, text='Camera Number')
        CameraLabel.grid(row=1, column=0)
        self.camNumber = IntVar()
        entryCam = Entry(bottomframe1, textvariable=self.camNumber)
        entryCam.grid(row=1, column=1)
        self.camNumber.set(self.controller.trackSettings["camera"])
        self.camNumber.trace("w", self.setCamera)

        ComLabel = Label(bottomframe1, text='COM Port')
        ComLabel.grid(row=2, column=0)
        self.comNumber = IntVar()
        entryCom = Entry(bottomframe1, textvariable=self.comNumber)
        entryCom.grid(row=2, column=1)
        self.comNumber.set(self.controller.trackSettings["comPort"])
        self.comNumber.trace("w", self.setComPort)

        labelLat = Label(bottomframe1, text='Latitude (N+)')
        labelLat.grid(row=3, column=0)
        self.latVal = DoubleVar()
        self.latVal.set(self.controller.trackSettings["Lat"])
        self.latVal.trace("w", self.setLat)
        entryLat = Entry(bottomframe1, textvariable=self.latVal)
        entryLat.grid(row=3, column=1)

        labelLon = Label(bottomframe1, text='Longitude (E+)')
        labelLon.grid(row=4, column=0)
        self.lonVal = DoubleVar()
        self.lonVal.set(self.controller.trackSettings["Lon"])
        self.lonVal.trace("w", self.setLon)
        entryLon = Entry(bottomframe1, textvariable=self.lonVal)
        entryLon.grid(row=4, column=1)

    def closeSettings(self):
        self.destroy()

    # noinspection PyUnusedLocal
    def setLat(self, *args):
        self.controller.trackSettings["Lat"] = varGetOrDefault(self.latVal, 0.0)

    # noinspection PyUnusedLocal
    def setLon(self, *args):
        self.controller.trackSettings["Lon"] = varGetOrDefault(self.lonVal, 0.0)

    # noinspection PyUnusedLocal
    def setComPort(self, *args):
        self.controller.trackSettings["comPort"] = varGetOrDefault(self.comNumber, 0)

    # noinspection PyUnusedLocal
    def setCamera(self, *args):
        self.controller.trackSettings["camera"] = varGetOrDefault(self.camNumber, 0)


class ImageRenderer(ImageCapture.ImageObserver):
    def __init__(self, imageElement, parent, displayFPS) -> None:
        super().__init__()
        self.imageElement = imageElement
        self.lastUpdate = 0
        self.lastUIUpdate = 0
        self.framesCaptured = 0
        self.parent = parent
        self.displayFPS = displayFPS

    def processingStarted(self) -> None:
        pass

    def imageCaptured(self, img: ImageCapture.Image) -> None:
        if img.captureTime - self.lastUIUpdate > 1/self.displayFPS:
            self.lastUIUpdate = img.captureTime
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
