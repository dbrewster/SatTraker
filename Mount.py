from abc import ABC, abstractmethod
import win32com.client
import math


class Mount(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def slewToRadCoordinates(self, coords) -> None:
        pass

    @abstractmethod
    def abortSlew(self) -> None:
        pass


class AscomEQ(Mount):
    def __init__(self) -> None:
        super().__init__()
        self.tel = None
        self.axis_ra_rate = 0.0
        self.axis_dec_rate = 0.0

    def connect(self) -> bool:
        driver = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        driver.DeviceType = 'Telescope'
        driverName = driver.Choose("None")
        self.tel = win32com.client.Dispatch(driverName)
        if not self.tel.Connected:
            self.tel.Connected = True
            axis = self.tel.CanMoveAxis(0)
            axis2 = self.tel.CanMoveAxis(1)
            if axis is False or axis2 is False:
                print('This scope cannot use the MoveAxis method, aborting.  DriverName=' + driverName)
                return False
            else:
                self.tel.Connected = True
                self.axis_ra_rate = float(self.tel.AxisRates(0).Item(1).Maximum)
                self.axis_dec_rate = float(self.tel.AxisRates(1).Item(1).Maximum)
                return True

    def disconnect(self) -> None:
        if self.tel and self.tel.Connected:
            self.tel.AbortSlew()
            self.tel.Connected = False

    # coords are a tuple of (ra, dec)
    def slewToRadCoordinates(self, coords) -> None:
        self.tel.SlewToCoordinates((math.degrees(coords[0]) / 15), math.degrees(coords[1]))

    def abortSlew(self) -> None:
        if self.tel:
            self.tel.AbortSlew()
