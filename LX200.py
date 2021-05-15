import time
import math
import serial

class LX200Track:
    def rad_to_sexagesimal_alt(self):
        self.azdeg = math.degrees(self.radaz)
        self.altdeg = math.degrees(self.radalt)
        self.az_d = math.trunc((self.azdeg))
        self.az_m = math.trunc((((self.azdeg)) - self.az_d) * 60)
        self.az_s = (((((self.azdeg)) - self.az_d) * 60) - self.az_m) * 60

        self.alt_d = math.trunc(self.altdeg)
        self.alt_m = math.trunc((abs(self.altdeg) - abs(self.alt_d)) * 60)
        self.alt_s = (((abs(self.altdeg) - abs(self.alt_d)) * 60) - abs(self.alt_m)) * 60

    def rad_to_sexagesimal_ra(self):
        self.rahour = math.degrees(self.radra) / 15
        self.decdeg = math.degrees(self.raddec)
        self.ra_h = math.trunc((self.rahour))
        self.ra_m = math.trunc((((self.rahour)) - self.ra_h) * 60)
        self.ra_s = (((((self.rahour)) - self.ra_h) * 60) - self.ra_m) * 60

        self.dec_d = math.trunc(self.decdeg)
        self.dec_m = math.trunc((abs(self.decdeg) - abs(self.dec_d)) * 60)
        self.dec_s = (((abs(self.decdeg) - abs(self.dec_d)) * 60) - abs(self.dec_m)) * 60

    def set_tracking(self, trackSettings):
        if trackSettings.tracking is False:
            try:
                self.comport = str('COM'+str(self.entryCom.get()))
                self.ser = serial.Serial(self.comport, baudrate=9600, timeout=1, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False)
                self.ser.write(str.encode(':U#'))
                self.serialconnected = True
                self.startButton5.configure(text='Disconnect Scope')
            except:
                print('Failed to connect on ' + self.comport)
                self.textbox.insert(END, str('Failed to connect on ' + str(self.comport) + '\n'))
                self.textbox.see('end')
                trackSettings.tracking = False
                return
        else:
            if self.serialconnected is True:
                self.ser.write(str.encode(':Q#'))
                self.ser.write(str.encode(':U#'))
                self.ser.close()
                self.serialconnected = False

    def firstTrack(self, trackSettings):
        if trackSettings.mountType == 'AltAz':
            sataz = math.degrees(self.sat.az) + 180
            if sataz > 360:
                sataz = sataz - 360
            sataz = math.radians(sataz)
            self.radaz = sataz
            self.rad_to_sexagesimal_alt()
            targetcoordaz = str(':Sz ' + str(self.az_d) + '*' + str(self.az_m) + ':' + str(int(self.az_s)) + '#')
            targetcoordalt = str(':Sa ' + str(self.alt_d) + '*' + str(self.alt_m) + ':' + str(int(self.alt_s)) + '#')
            self.ser.write(str.encode(targetcoordaz))
            self.ser.write(str.encode(targetcoordalt))
            self.ser.write(str.encode(':MA#'))
            print(targetcoordaz, targetcoordalt)
            self.textbox.insert(END, str('Az: ' + str(targetcoordaz) + 'Alt: ' + str(targetcoordalt) + '\n'))
            self.textbox.see('end')
        if trackSettings.mountType == 'Eq':
            satra = self.sat.ra
            self.radra = self.sat.ra
            self.raddec = self.sat.dec
            self.rad_to_sexagesimal_ra()
            targetcoordra = str(':Sr ' + str(self.ra_h) + '*' + str(self.ra_m) + ':' + str(int(self.ra_s)) + '#')
            targetcoorddec = str(':Sd ' + str(self.dec_d) + '*' + str(self.dec_m) + ':' + str(int(self.dec_s)) + '#')
            self.ser.write(str.encode(targetcoordra))
            self.ser.write(str.encode(targetcoorddec))
            self.ser.write(str.encode(':MS#'))
            print(targetcoordra, targetcoorddec)
            self.textbox.insert(END, str('RA: ' + str(targetcoordra) + 'Dec: ' + str(targetcoorddec) + '\n'))
            self.textbox.see('end')
        time.sleep(1)
        # Do alt degrees twice to clear the buffer cause I'm too lazy to clear the buffer properly
        self.LX200_alt_degrees()
        self.LX200_alt_degrees()
        currentalt = self.telalt
        self.LX200_az_degrees()
        currentaz = self.telaz
        altdiff = math.degrees(self.radalt) - currentalt
        azdiff = math.degrees(self.radaz) - currentaz
        totaldiff = math.sqrt(altdiff ** 2 + azdiff ** 2)
        self.lasttotaldiff = totaldiff
        self.dlast = self.dnow
        while totaldiff > 1:
            self.LX200_alt_degrees()
            self.LX200_alt_degrees()
            currentalt = self.telalt
            self.LX200_az_degrees()
            currentaz = self.telaz
            altdiff = math.degrees(self.radalt) - currentalt
            azdiff = math.degrees(self.radaz) - currentaz
            totaldiff = math.sqrt(altdiff ** 2 + azdiff ** 2)
            time.sleep(1)
