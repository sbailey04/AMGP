################################################
#                                              #
#       Automated Map Generation Program       #
#             Utilities Module                 #
#            Author: Sam Bailey                #
#        Last Revised: Apr 12, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
import math
import sys
import os
import contextlib
from PIL import Image as PImage
from PIL import ImageDraw, ImageFont, ImageFilter

#----------------- AMGP IMPORTS -------------------#



#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_UTIL",
            'priority':0,
            'type':0}

class Time(object):
    def __init__(self, plotType, Date, currentTime, timeMode, convMode):
        
        timeFormat = None
        convFormat = None
        rec = False
        
        timeFormats = {0:[8], # Precise to the hour
                       1:[0, 1], # Precise to three hours - used by surface obs
                       2:[3, 4, 5, 6, 7], # Precise to six hours - used by gridded reanalysis data
                       3:[2, 13], # Precise to twelve hours - used by upper-air obs and Skew-Ts
                       4:[], # Precise to twenty four hours
                       5:[9], # Convective outlook day 1
                       6:[10], # Convective outlook day 2
                       7:[11], # Convective outlook day 3
                       8:[12]} # Probabalistic outlooks days 4-8
                            # Satellite data is taken VERY frequently,
                            # and pulls the closest one to the time it's given,
                            # so it can use any of these time formats.
                            # However, it's default time format is 0, simply so that
                            # the rest of the code doesn't die horribly if sat
                            # data is the only data called for.
        
        for value in plotType:
            for i in range(0, 5):
                if value in timeFormats[i]:
                    timeFormat = i
        
        for value in plotType:
            for i in range(5, 9):
                if value in timeFormats[i]:
                    convFormat = i
        
        splitDate = Date.split(", ")
        if splitDate[0] == 'recent':
            givenTime = currentTime
        elif splitDate[0] == 'today':
            givenTime = datetime(currentTime.year, currentTime.month, currentTime.day, int(splitDate[1]))
        else:
            givenTime = datetime(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]), int(splitDate[3]))
            
        recentness = currentTime - givenTime
        if recentness < timedelta(hours=3):
            flag = 1
            flag2 = 1
        elif recentness < timedelta(hours=6):
            flag = 0
            flag2 = 1
        else:
            flag = 0
            flag2 = 0
           
        
        if not rec:
            if (givenTime < datetime(1931, 1, 2)):
                sys.exit("<error> The date you entered is out of range!")
            if (givenTime < datetime(1979, 1, 1)):
                print("<warning> The date you entered is out of range for gridded data.")
            if (givenTime < datetime(2003, 1, 23)):
                print("<warning> The date you entered is out of range for convective outlooks.")
            if ((recentness) > timedelta(days=13)):
                print("<warning> The date you entered is out of range for satelite scans.")
        
        if (timeMode == 'raw') or (timeFormat == None):
            self.category = "raw"
            self.time = givenTime
            # This is basically only good for satelite data when "recent" is used.
        elif timeMode == 'async':
            self.onetime = datetime(givenTime.year, givenTime.month, givenTime.day, math.floor(givenTime.hour))
            for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                if givenTime.hour >= hour:
                    Hour = hour
                    self.threetime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            for hour in [18, 12, 6, 0]:
                if givenTime.hour >= hour + 6 * flag2:
                    Hour = hour
                    self.sixtime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            if givenTime.hour < 6:
                Hour = 18
                self.sixtime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            for hour in [12, 0]:
                if givenTime.hour >= hour + 3 * flag:
                    Hour = hour
                    self.twelvetime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            self.twentyfourtime = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
        elif timeMode == 'sync':
            self.category = "sync"
            Hour = 0
            if timeFormat == 4:
                self.time = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
            elif timeFormat == 3:
                for hour in [12, 0]:
                    if givenTime.hour >= hour + 3 * flag:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 2:
                for hour in [18, 12, 6, 0]:
                    if givenTime.hour >= hour + 6 * flag2:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
                if givenTime.hour < 6:
                    Hour = 18
                    self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            elif timeFormat == 1:
                for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                    if givenTime.hour >= int(hour):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 0:
                self.time = datetime(givenTime.year, givenTime.month,givenTime.day, math.floor(givenTime.hour))
        elif timeMode == 'near':
            self.category = "near"
            Hour = 0
            if timeFormat == 0:
                self.time = datetime(givenTime.year, givenTime.month,givenTime.day, math.floor(givenTime.hour))
            elif timeFormat == 1:
                for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                    if givenTime.hour >= hour:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 2:
                for hour in [18, 12, 6, 0]:
                    if givenTime.hour >= hour + 6 * flag2:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
                if givenTime.hour < 6:
                    Hour = 18
                    self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            elif timeFormat == 3:
                for hour in [12, 0]:
                    if givenTime.hour >= hour + 3 * flag:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 4:
                self.time = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
        
        if len(splitDate) == 5:
            self.minutes = splitDate[4]
        else:
            self.minutes = 0
        
        if timeMode == "async":
            if timeFormat == 0:
                self.category = "async-1"
                self.ds = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}"
                self.tsnum = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}-{self.onetime.strftime('%H')}Z"
                self.tsalp = f"{self.onetime.strftime('%b')} {self.onetime.day}, {self.onetime.year} - {self.onetime.hour}Z"
                self.recentness = currentTime - self.onetime
            elif timeFormat == 1:
                self.category = "async-3"
                self.ds = f"{self.threetime.year}-{self.threetime.strftime('%m')}-{self.threetime.strftime('%d')}"
                self.tsnum = f"{self.threetime.year}-{self.threetime.strftime('%m')}-{self.threetime.strftime('%d')}-{self.threetime.strftime('%H')}Z"
                self.tsalp = f"{self.threetime.strftime('%b')} {self.threetime.day}, {self.threetime.year} - {self.threetime.hour}Z"
                self.recentness = currentTime - self.threetime
            elif timeFormat == 2:
                self.category = "async-6"
                self.ds = f"{self.sixtime.year}-{self.sixtime.strftime('%m')}-{self.sixtime.strftime('%d')}"
                self.tsnum = f"{self.sixtime.year}-{self.sixtime.strftime('%m')}-{self.sixtime.strftime('%d')}-{self.sixtime.strftime('%H')}Z"
                self.tsalp = f"{self.sixtime.strftime('%b')} {self.sixtime.day}, {self.sixtime.year} - {self.sixtime.hour}Z"
                self.recentness = currentTime - self.sixtime
            elif timeFormat == 3:
                self.category = "async-12"
                self.ds = f"{self.twelvetime.year}-{self.twelvetime.strftime('%m')}-{self.twelvetime.strftime('%d')}"
                self.tsnum = f"{self.twelvetime.year}-{self.twelvetime.strftime('%m')}-{self.twelvetime.strftime('%d')}-{self.twelvetime.strftime('%H')}Z"
                self.tsalp = f"{self.twelvetime.strftime('%b')} {self.twelvetime.day}, {self.twelvetime.year} - {self.twelvetime.hour}Z"
                self.recentness = currentTime - self.twelvetime
            elif timeFormat == 4:
                self.category = "async-24"
                self.ds = f"{self.twentyfourtime.year}-{self.twentyfourtime.strftime('%m')}-{self.twentyfourtime.strftime('%d')}"
                self.tsnum = f"{self.twentyfourtime.year}-{self.twelvettwentyfourtimeime.strftime('%m')}-{self.twentyfourtime.strftime('%d')}-{self.twentyfourtime.strftime('%H')}Z"
                self.tsalp = f"{self.twentyfourtime.strftime('%b')} {self.twentyfourtime.day}, {self.twentyfourtime.year} - {self.twentyfourtime.hour}Z"
                self.recentness = currentTime - self.twentyfourtime
        else:
            self.ds = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}"
            self.tsnum = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}-{self.time.strftime('%H')}Z"
            self.tsalp = f"{self.time.strftime('%b')} {self.time.day}, {self.time.year} - {self.time.hour}Z"
            self.recentness = currentTime - self.time
        
        try:
            self.tsfull = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}-{self.time.strftime('%H%M')}Z"
        except AttributeError:
            self.tsfull = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}-{self.onetime.strftime('%H%M')}Z"
        
        if convMode == "recent":
            if convFormat == 5:
                if givenTime.hour > 20:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                elif givenTime.hour + (givenTime.minute / 60) > 16.5:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 16, 30)
                elif givenTime.hour > 13:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 13, 0)
                elif givenTime.hour > 12:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 12, 0)
                elif givenTime.hour > 1:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 1, 0)
                else:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0) - timedelta(days=1)
            if convFormat == 6:
                if givenTime.hour + (givenTime.minute / 60) > 17.5:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                elif givenTime.hour > 6:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 6, 0)
                else:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30) - timedelta(days=1)
            if convFormat == 7:
                if givenTime.hour + (givenTime.minute / 60) > 7.5:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                else:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30) - timedelta(days=1)
            if convFormat == 8:
                if givenTime.hour > 9:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day, 3)
                else:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day) - timedelta(days=1)
        elif convMode == "latest":
            if currentTime - givenTime > timedelta(days=1):
                if convFormat == 5:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                if convFormat == 6:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                if convFormat == 7:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                if convFormat == 8:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day)
            else:
                if convFormat == 5:
                    if givenTime.hour > 20:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                    elif givenTime.hour + (givenTime.minute / 60) > 16.5:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 16, 30)
                    elif givenTime.hour > 13:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 13, 0)
                    elif givenTime.hour > 12:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 12, 0)
                    elif givenTime.hour > 1:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 1, 0)
                    else:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0) - timedelta(days=1)
                if convFormat == 6:
                    if givenTime.hour + (givenTime.minutes / 60) > 17.5:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                    elif givenTime.hour > 6:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 6, 0)
                    else:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30) - timedelta(days=1)
                if convFormat == 7:
                    if givenTime.hour + (givenTime.minute / 60) > 7.5:
                        self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                    else:
                        self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30) - timedelta(days=1)
                if convFormat == 8:
                    if givenTime.hour > 9:
                        self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day)
                    else:
                        self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day) - timedelta(days=1)
        
        self.timeformat = timeFormat
        self.convformat = convFormat
        
        self.now = currentTime
                
        #elif convMode == "auto":
        #    if convFormat == 5:
        #        
        #    if convFormat == 6:
        #        
        #    if convFormat == 7:
                
                
            
            
            
        
        
        
    def ToString(self):
        return f"{self.time.year}, {self.time.month}, {self.time.day}, {self.time.hour}"
    
    def WithMinutes(self):
        return datetime(self.time.year, self.time.month, self.time.day, self.time.hour, self.minutes)
    

def ParseTime(plotType, string, currentTimeObj, timeMode, convMode):
    return Time(plotType, string, currentTimeObj, timeMode, convMode)

def FromDatetime(plotType, datetimeObj, currentTimeObj, timeMode, convMode):
        customTimeFormat = f"{datetimeObj.year}, {datetimeObj.month}, {datetimeObj.day}, {datetimeObj.hour}"
        newTime = ParseTime(plotType, customTimeFormat, currentTimeObj, timeMode, convMode)
        return newTime
    
    

class Levels(object):
    def __init__(self, lvlstring):
        
        self.mslp_formatter = lambda v: format(v*10, '.0f')[-3:]
        
        if lvlstring != 'surface':
            lvlstring = int(lvlstring)
            if (lvlstring == 975) or (lvlstring == 850) or (lvlstring == 700):
                self.height_format = lambda v: format(v, '.0f')[1:]
                self.steps = 30
            elif lvlstring == 500:
                self.height_format = lambda v: format(v, '.0f')[:-1]
                self.steps = 60
            elif lvlstring == 300:
                self.height_format = lambda v: format(v, '.0f')[:-1]
                self.steps = 120
            elif lvlstring == 200:
                self.height_format = lambda v: format(v, '.0f')[1:-1]
                self.steps = 120
                
            self.level = int(lvlstring)
        else:
            self.level = lvlstring

def GetLevel(lvlstring):
    return Levels(lvlstring)

def setTime():
    currentTime = datetime.utcnow()
    return currentTime
    
def getTime():
    currentTime = datetime.utcnow()
    print(f"<time> It is currently {currentTime}Z")
    return currentTime

def ClearTemp():
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
    for subPath in os.listdir(f"{dr}/Temp"):
        if os.path.isdir(f"{dr}/Temp/{subPath}"):
            ClearTemp(f"{dr}/Temp/{subPath}")
            os.rmdir(f"{dr}/Temp/{subPath}")
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"{dr}/Temp/{subPath}")

def Watermark(save, version):
    wid, hei = save.size
    if wid > hei:
        sz = (int(hei * 0.8), int(hei * 0.8))
    if hei > wid:
        sz = (int(wid * 0.8), int(wid * 0.8))
    sz1, sz2 = sz
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "")
    wm = PImage.open(f'{dr}/Resources/logo.png')
    wm = wm.convert('RGBA').resize(sz)
    wm.putalpha(int(0.1*255))
    left = int((wid-sz1) / 2)
    top = int((hei-sz1) / 2)
    save.paste(wm, (left, top), wm)
    return save