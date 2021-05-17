from tkinter import *
from tkinter import filedialog

import cv2
import numpy as np
from PIL import Image as PILImage, ImageTk

import ImageCapture
from Controller import Controller
from SettingsPopup import SettingsPopup
from Mount import AscomEQ


def blankImage(width, height):
    blank_image = np.zeros((height, width, 3), np.uint8)
    local_tkimg = PILImage.fromarray(blank_image)
    local_tkimg = ImageTk.PhotoImage(image=local_tkimg)
    return local_tkimg


# noinspection PyPep8Naming,PyMethodMayBeStatic,SpellCheckingInspection
class Buttons:
    def __init__(self, master):
        self.controller = Controller()
        self.controller.readConfig()
        self.imageCapture = None
        self.master = master
        self.listener = None
        self.mount = None

        master.winfo_toplevel().title("SatTraker")
        master.protocol("WM_DELETE_WINDOW", self.onClose)

        master.geometry(str(self.controller.get("windowwidth")) + "x" + str(self.controller.get("windowheight")))

        master.bind("<Configure>", self.setWindowSize)

        self.buttonFrame = Frame(master, height=32, bg="black")
        self.buttonFrame.pack(side=TOP, fill="x")
        self.buttonFrame.grid_propagate(False)

        buttons = Frame(self.buttonFrame, bg="black")
        buttons.pack(side=TOP, anchor='e')
        startCamera = PILImage.open("./start_camera.png").resize((30, 30))
        self.startCameraButton = ImageTk.PhotoImage(startCamera)
        stopCamera = PILImage.open("./stop_camera.png").resize((30, 30))
        self.stopCameraButton = ImageTk.PhotoImage(stopCamera)
        self.startButton = Button(buttons, image=self.startCameraButton, command=self.set_img_collect, highlightthickness=0, bd=0)
        self.startButton.grid(row=0, column=0, padx=4, pady=4)

        connectMount = PILImage.open("./connect_mount.png").resize((30, 30))
        self.connectMountImg = ImageTk.PhotoImage(connectMount)
        disconnectMount = PILImage.open("./disconnect_mount.png").resize((30, 30))
        self.disconnectMountImg = ImageTk.PhotoImage(disconnectMount)
        self.mountButton = Button(buttons, image=self.connectMountImg, command=self.connectMount, highlightthickness=0, bd=0)
        self.mountButton.grid(row=0, column=1, padx=4, pady=4)

        self.fpsElement = Label(self.buttonFrame, fg="white", bg="black", highlightthickness=0, bd=0)
        self.fpsElement.place(x=5, y=8)

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
        self.controller.set("windowwidth", self.master.winfo_width())
        self.controller.set("windowheight", self.master.winfo_height())

    def setNoFlip(self):
        self.controller.set("flip", 'NoFlip')

    def setVerticalFlip(self):
        self.controller.set("flip", 'VerticalFlip')

    def setHorizontalFlip(self):
        self.controller.set("flip", 'HorizontalFlip')

    def setVerticalHorizontalFlip(self):
        self.controller.set("flip", 'VerticalHorizontalFlip')

    def set0Rotate(self):
        self.controller.set("rotate", 0)

    def setPos90Rotate(self):
        self.controller.set("rotate", 90)

    def setNeg90Rotate(self):
        self.controller.set("rotate", -90)

    def set180Rotate(self):
        self.controller.set("rotate", 180)

    def exitProg(self):
        if self.collect_images:
            self.set_img_collect()
        self.controller.writeConfig()
        sys.exit()

    def filePicker(self):
        self.controller.set("orbitFile", filedialog.askopenfilename(initialdir=".", title="Select TLE file", filetypes=(("text files", "*.txt"), ("tle files", "*.tle"), ("all files", "*.*"))))
        self.controller.set("fileSelected", True)
        print(self.controller.get("orbitFile"))

    def set_center(self):
        self.controller.set("setcenter", True)

    def setLX200AltAz(self):
        self.controller.set("telescopeType", 'LX200')
        self.controller.set("mountType", 'AltAz')

    def setLX200Eq(self):
        self.controller.set("telescopeType", 'LX200')
        self.controller.set("mountType", 'Eq')

    def setFeatureTrack(self):
        self.controller.set("trackingtype", 'Features')

    def setBrightTrack(self):
        self.controller.set("trackingtype", 'Bright')

    def setASCOMAltAz(self):
        self.controller.set("telescopeType", 'ASCOM')
        self.controller.set("mountType", 'AltAz')

    def setASCOMEq(self):
        self.controller.set("telescopeType", 'ASCOM')
        self.controller.set("mountType", 'Eq')

    # noinspection PyUnusedLocal
    def goup(self, event):
        pass
        # self.controller.trackSettings["mainviewY"] -= 1
        # self.imageCapture.incExposure()

    # noinspection PyUnusedLocal
    def godown(self, event):
        pass
        # self.controller.trackSettings["mainviewY"] += 1
        # self.imageCapture.decExposure()

    # noinspection PyUnusedLocal
    def goleft(self, event):
        # self.controller.get("mainviewX") -= 1
        pass

    # noinspection PyUnusedLocal
    def goright(self, event):
        # self.controller.get("mainviewX") += 1
        pass

    def connectMount(self):
        if self.mount:
            self.mount.disconnect()
            self.mount = None
            self.mountButton.config(image=self.connectMountImg)
        else:
            self.mount = AscomEQ()
            if not self.mount.connect():
                print("Could not connect mount")
                self.mount = None
            else:
                self.mountButton.config(image=self.disconnectMountImg)

    def start_sat_track(self):
        pass

    def sat_track(self):
        pass

    def start_calibration(self):
        pass

    def set_img_collect(self):
        if self.collect_images:
            self.listener = None
            self.startButton.configure(image=self.startCameraButton)
            self.imageCapture.stopCapture()
            self.collect_images = False
        else:
            self.startButton.configure(image=self.stopCameraButton)
            self.imageCapture = ImageCapture.ImageCapture(self.controller)

            self.imageCapture.addObserver(ImageRenderer(self.displayimg, self.fpsElement, self.cameraFrame, self.controller))
            self.imageCapture.startCaputure()
            self.collect_images = True


class ImageRenderer(ImageCapture.ImageObserver):
    def __init__(self, imageElement, fpsElement, parent, controller) -> None:
        super().__init__()
        self.imageElement = imageElement
        self.lastUpdate = 0
        self.lastUIUpdate = 0
        self.framesCaptured = 0
        self.parent = parent
        self.controller = controller
        self.fpsElement = fpsElement

    def processingStarted(self) -> None:
        pass

    def imageCaptured(self, img: ImageCapture.Image) -> None:
        displayFPS = self.controller.get("refreshRate")
        if displayFPS < 1:
            displayFPS = 1
        if img.captureTime - self.lastUIUpdate > 1/displayFPS:
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
            self.fpsElement.config(text="FPS: {:.3f}".format(self.framesCaptured / (img.captureTime - self.lastUpdate)))
            # print("frames per sec = " + str(self.framesCaptured / (img.captureTime - self.lastUpdate)))
            self.framesCaptured = 0
            self.lastUpdate = img.captureTime

    def processingDone(self) -> None:
        self.imageElement.config(image="")
        self.imageElement.pack(side=TOP, fill="both", expand=True)
        self.fpsElement.config(text="")


root = Tk()
b = Buttons(root)
root.mainloop()
