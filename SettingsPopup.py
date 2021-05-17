from tkinter import Frame, Button, BOTTOM, Label, IntVar, Entry, DoubleVar, Scale
from PIL import ImageTk, Image as PILImage


def varGetOrDefault(var, default):
    try:
        return var.get()
    except:
        return default


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
        self.camNumber.set(self.controller.get("camera"))
        self.camNumber.trace("w", self.setCamera)

        ComLabel = Label(bottomframe1, text='COM Port')
        ComLabel.grid(row=2, column=0)
        self.comNumber = IntVar()
        entryCom = Entry(bottomframe1, textvariable=self.comNumber)
        entryCom.grid(row=2, column=1)
        self.comNumber.set(self.controller.get("comPort"))
        self.comNumber.trace("w", self.setComPort)

        labelLat = Label(bottomframe1, text='Latitude (N+)')
        labelLat.grid(row=3, column=0)
        self.latVal = DoubleVar()
        self.latVal.set(self.controller.get("Lat"))
        self.latVal.trace("w", self.setLat)
        entryLat = Entry(bottomframe1, textvariable=self.latVal)
        entryLat.grid(row=3, column=1)

        labelLon = Label(bottomframe1, text='Longitude (E+)')
        labelLon.grid(row=4, column=0)
        self.lonVal = DoubleVar()
        self.lonVal.set(self.controller.get("Lon"))
        self.lonVal.trace("w", self.setLon)
        entryLon = Entry(bottomframe1, textvariable=self.lonVal)
        entryLon.grid(row=4, column=1)

        def getExposureStr(strValue):
            value = float(strValue)
            if value > 0:
                return "{:.3f}".format(pow(2, value))
            else:
                return "1/{:.3f}".format(pow(2, abs(value)))

        def setExposureValue(strValue):
            value = float(strValue)
            self.controller.set("exposure", value)
            self.labelExposureVal.config(text=getExposureStr(value))

        labelExposure = Label(bottomframe1, text="Exposure (s)")
        labelExposure.grid(row=5, column=0)
        self.labelExposureVal = Label(bottomframe1, text=getExposureStr(self.controller.get("exposure")))
        self.labelExposureVal.grid(row=5, column=1)

        exposure = Scale(bottomframe1, from_=-15, to=5, resolution=.1, orient="horizontal", showvalue=0, command=setExposureValue)
        exposure.grid(row=6, column=0, columnspan=2, sticky="nesw")
        exposure.set(self.controller.get("exposure"))

        def setGainValue(strValue):
            value = int(strValue)
            self.controller.set("gain", value)
            self.labelGainVal.config(text=str(value))

        labelGain = Label(bottomframe1, text="Gain")
        labelGain.grid(row=7, column=0)
        self.labelGainVal = Label(bottomframe1, text=str(self.controller.get("gain")))
        self.labelGainVal.grid(row=7, column=1)

        gain = Scale(bottomframe1, from_=0, to=300, orient="horizontal", showvalue=0, command=setGainValue)
        gain.grid(row=8, column=0, columnspan=2, sticky="nesw")
        gain.set(self.controller.get("gain"))

        def setRefreshRate(strValue):
            value = int(strValue)
            self.controller.set("refreshRate", value)
            self.labelRefreshRateVal.config(text=str(value))

        labelRefresh = Label(bottomframe1, text="Refresh Rate (FPS)")
        labelRefresh.grid(row=9, column=0)
        self.labelRefreshRateVal = Label(bottomframe1, text=str(self.controller.get("refreshRate")))
        self.labelRefreshRateVal.grid(row=9, column=1)

        refreshRate = Scale(bottomframe1, from_=1, to=60, orient="horizontal", showvalue=0, command=setRefreshRate)
        refreshRate.grid(row=10, column=0, columnspan=2, sticky="nesw")
        refreshRate.set(self.controller.get("refreshRate"))

    def closeSettings(self):
        self.destroy()

    # noinspection PyUnusedLocal
    def setLat(self, *args):
        self.controller.set("Lat", varGetOrDefault(self.latVal, 0.0))

    # noinspection PyUnusedLocal
    def setLon(self, *args):
        self.controller.set("Lon", varGetOrDefault(self.lonVal, 0.0))

    # noinspection PyUnusedLocal
    def setComPort(self, *args):
        self.controller.set("comPort", varGetOrDefault(self.comNumber, 0))

    # noinspection PyUnusedLocal
    def setCamera(self, *args):
        self.controller.set("camera", varGetOrDefault(self.camNumber, 0))