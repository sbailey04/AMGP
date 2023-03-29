################################################
#                                              #
#       Automated Map Generation Program       #
#                                              #
#            Author: Sam Bailey                #
#        Last Revised: Mar 28, 2023            #
#                Version 0.3.0                 #
#                                              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
from io import StringIO
from urllib.request import urlopen
from siphon.simplewebservice.iastate import IAStateUpperAir
from siphon.catalog import TDSCatalog

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from metpy.io import add_station_lat_lon
from metpy.io import metar
from metpy.plots import declarative, PlotGeometry
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
import pandas as pd
import geopandas as gpd
from collections import Counter
import numpy as np
import math
import os
import sys
from PIL import Image
import json
import glob
import contextlib
from importlib import import_module

#from tkinter import *
#from tkinter import ttk

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)

from Modules import AMGP_UTIL as amgp

amgpmodules = []
amgpmodulenames = ["AMGP_UTIL"]

for module in os.listdir("Modules"):
    if (module != "AMGP_UTIL.py") and (module != ".ipynb_checkpoints") and (module != "__pycache__") and (module != "depreciated.py"):
        strp = module.replace(".py", '')
        var = strp.replace("_", '').lower()
        globals()[f"{var}"] = import_module(f'Modules.{strp}')
        print(f"<startup> {strp} imported as {var}")
        amgpmodules.append(globals()[f"{var}"])
        amgpmodulenames.append(f"{strp}")

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

version = "0.3.0"

presets = []

# Opening the config file and manual, and finding presets.
if os.path.isfile("config.json"):
    with open("config.json", "r") as cfg:
        config = json.load(cfg)

for folder in os.listdir("Presets"):
    for preset in os.listdir("Presets/" + folder):
        if preset.endswith('.json'):
            presets.append([f"{folder}-{preset.replace('.json','')}"])
        
if os.path.isfile("manual.txt"):
    with open("manual.txt", "r") as man:
        manual = man.readlines()
else:
    manual = ['Manual not found...']

    
# Retrieving and setting the current UTC time
def setTime():
    global currentTime
    currentTime = datetime.utcnow()
    
def getTime():
    global currentTime
    currentTime = datetime.utcnow()
    print(f"<time> It is currently {currentTime}Z")

# Definitions
def inputChain():
    global loaded
    global title
    global noShow
    
    print("<menu> Input commands, or type 'help'.")
    comm = input("<input> ")
    
    command = comm.split(" ")
    
    if command[0] == "help":
        for line in list(range(1, 58, 1)):
            print(manual[line], end='')
        inputChain()
    
    if command[0] == "list":
        print("<list> Type 'time' to set and print the current time.")
        print("<list> Type 'preset {name}' to load a map preset.")
        print("<list> Type 'preset list' to list available presets.")
        print("<list> Type 'factors' to list accepted map factors.")
        print("<list> Type 'paste' to see the currently loaded values.")
        print("<list> Type 'edit {parameter} {value}' to edit a loaded parameter.")
        print("<list> Type 'edit Factors {(optional) add/remove} {value}' to edit loaded factors.")
        print("<list> Type 'save {preset name}' to save the current settings as a preset.")
        print("<list> Type 'run' to run with the current settings.")
        print("<list> Type 'quit' to exit without running.")
        inputChain()
    
    
    if command[0] == 'time':
        getTime()
        inputChain()
#    elif command[0] == 'update':
#        cfgUpdate()
#        inputChain()
    elif command[0] == 'preset':
        if command[1] == 'list':
            for item in presets:
                spi = item.split("-")
                plotkeys = []
                multikeys = []
                skewtkeys = []
                if spi[0] == "plot":
                    plotkeys.append(spi[1])
                if spi[0] == "mmg":
                    plotkeys.append(spi[1])
                if spi[0] == "stlp":
                    plotkeys.append(spi[1])
            print("<presets> Below is the list of all currently loaded presets:")
            print("<presets> Plots: " + plotkeys)
            print("<presets> Multimode: " + multikeys)
            print("<presets> Skew-T: " + skewtkeys)
            inputChain()
        else:
            presetLoad(command[1])
            singleLoads()
            inputChain()
    elif command[0] == 'factors':
        for module in [amgpobs, amgpgrd, amgpsat, amgpconv]:
            module.factors()
        inputChain()
    elif command[0] == 'paste':
        singleLoads()
        inputChain()
    elif command[0] == 'edit':
        if command[1] in ["Level", "Date", "Delta", "Factors", "Area", "DPI", "Scale", "PRF", "BF", "Smooth", "Projection", "TM", "CM"]:
            if command[1] == "Level":
                loaded.update({'level':command[2]})
            if command[1] == "Date":
                if command[2] == 'recent':
                    loaded.update({'date':command[2]})
                elif command[2] == "today":
                    loaded.update({'date':f'{command[2]}, {command[3]}'})
                else:
                    loaded.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            if command[1] == "Delta":
                loaded.update({'delta':command[2]})
            if command[1] == "Factors":
                blankFactors = []
                count = 0
                if command[2] == "add":
                    blankFactors = loaded['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            blankFactors.append(command[count])
                        count += 1
                elif command[2] == "remove":
                    blankFactors = loaded['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            if command[count] in blankFactors:
                                blankFactors.pop(blankFactors.index(command[count]))
                            else:
                                print("<error> That is not a valid factor to remove!")
                                inputChain()
                        count += 1
                else:
                    for item in command:
                        if count > 1:
                            blankFactors.append(command[count])
                        count += 1
                fullFactors = ', '.join(blankFactors)
                loaded.update({'factors':fullFactors})
            if command[1] == "Area":
                loaded.update({'area':command[2]})
            if command[1] == "DPI":
                loaded.update({'dpi':command[2]})
            if command[1] == "Scale":
                loaded.update({'scale':command[2]})
            if command[1] == "PRF":
                loaded.update({'prfactor':command[2]})
            if command[1] == 'BF':
                loaded.update({'barbfactor':command[2]})
            if command[1] == "Smooth":
                loaded.update({'smoothing':command[2]})
            if command[1] == "Projection":
                loaded.update({'projection':command[2]})
            if command[1] == "TM":
                if command[2] not in ["raw","sync","async","near"]:
                    print("<error> That is not a valid value for the Time Mode!")
                    inputChain()
                loaded.update({'timemode':command[2]})
            if command[1] == "CM":
                if command[2] not in ["recent","latest"]:
                    print("<error> That is not a valid value for the Convective Mode!")
                    inputChain()
                loaded.update({'convmode':command[2]})
            singleLoads()
            inputChain()
        else:
            print("<error> That is not a valid parameter to edit!")
            inputChain()
    elif command[0] == 'save':
        save(f'{command[1]}')
        print(f"<save> Loaded settings saved to Presets/plot as preset: {command[1]}.json")
        inputChain()
    elif command[0] == 'run':
        dosave = input("<run> Would you like to save this map? [y/n] ")
        if dosave == 'y':
            S = True
            NS = input("<run> Would you like to show this map? [y/n] ")
            if NS == 'n':
                noShow = True
            else:
                noShow = False
            title = input("<run> If you would like to override the default title, type the override here. Otherwise, hit enter: ")
        else:
            S = False
            title = ''
        save('prev')
        print("<run> Previous settings saved.")
        if os.path.isdir("Maps/Temp"):
            ClearTemp()
        product = run(loaded, title)
        SaveMap(product, S, noShow)
        inputChain()
    elif command[0] == 'mode':
        global mode
        if command[1] == "multi":
            mode = 1
            multiMode()
        elif command[1] == "skewt":
            mode = 2
            stlpMode()
    elif command[0] == 'quit':
        ClearTemp()
        sys.exit("<quit> The process was terminated.")
    else:
        print("<error> That is not a valid command!")
        inputChain()
        
#      ------ End inputChain() ------

# Update the current config file from 0.1.0 to 0.2.0
def cfgUpdate(ver):
    for base in config:
        if base == 'presets':
            fullData = config[base]
    config['presets'] = {'plots':{},'skewt':{}}
    config['presets']['plots'] = fullData
    config['config_ver'] = version
    with open("config.json", "w") as J:
        json.dump(config, J)

        
# Save a preset to the config file

def save(name):
    saveState = {"level":f"{loaded['level']}","date":f"{loaded['date']}","delta":f"{loaded['delta']}","factors":f"{loaded['factors']}","area":f"{loaded['area']}","dpi":f"{loaded['dpi']}","scale":f"{loaded['scale']}","prfactor":f"{loaded['prfactor']}","barbfactor":f"{loaded['barbfactor']}","smoothing":f"{loaded['smoothing']}","projection":f"{loaded['projection']}","timemode":f"{loaded['timemode']}","convmode":f"{loaded['convmode']}"}
    data = {"amgp_ver":version,"type":"obs","settings":saveState}
    
    if os.path.isfile(f"Presets/plot/{name}.json"):
        os.remove(f"Presets/plot/{name}.json")
    
    with open(f"Presets/plot/{name}.json", "a") as J:
        json.dump(data, J)

# Load a preset from the config file
def presetLoad(loadedPreset):
    global loaded
    with open(f"Presets/plot/{loadedPreset}.json", "r") as J:
        lo = json.load(J)
        loaded = lo["settings"]
    
def setInit():
    global Set
    Set = {'date':'recent','delta':0,'jump':3,'levels':'surface','dloop':0,'fcloop':0}
    
# Dump the loaded preset's contents
def singleLoads():
    print(f"<loaded> Level: {loaded['level']}")
    print(f"<loaded> Date: {loaded['date']}")
    print(f"<loaded> Delta: {loaded['delta']}")
    print(f"<loaded> Factors: {loaded['factors']}")
    print(f"<loaded> Area: {loaded['area']}")
    print(f"<loaded> DPI: {loaded['dpi']}")
    print(f"<loaded> Scale: {loaded['scale']}")
    print(f"<loaded> PRF (Point Reduction Scale): {loaded['prfactor']}")
    print(f"<loaded> BF (Barb Factor): {loaded['barbfactor']}")
    print(f"<loaded> Smooth: {loaded['smoothing']}")
    print(f"<loaded> Projection: {loaded['projection']}")
    print(f"<loaded> TM (Time Mode): {loaded['timemode']}")
    print(f"<loaded> CM (Convective Mode): {loaded['convmode']}")

def multiLoads():
    print(f"<settings> Below are the settings from the loaded preset:")
    singleLoads()
    print(f"<settings> Below are the settings from the current multiRun settings:")
    print(f"<settings> Date: {Set['date']}")
    print(f"<settings> DLoop: {Set['dloop']}")
    print(f"<settings> Delta: {Set['delta']}")
    print(f"<settings> Jump: {Set['jump']}")
    print(f"<settings> Levels: {Set['levels']}")
    print(f"<settings> FCLoop: {Set['fcloop']}")

def ClearTemp():
    for subPath in os.listdir(f"Maps/Temp"):
        if os.path.isdir(f"Maps/Temp/{subPath}"):
            ClearTemp(f"Maps/Temp/{subPath}")
            os.rmdir(f"Maps/Temp/{subPath}")
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"Maps/Temp/{subPath}")
                
def PullFactors(values):
    
    factorList = values['factors'].split(', ')
    
    plotType = []
    
    for factor in factorList:
        for module in amgpmodules:
            if factor in module.getFactors().keys():
                plotType.append(module.getFactors()[f'{factor}'])
                
    if (values['level'] == 'surface') and (0 in plotType):
        plotType.append(1)
    if (values['level'] != 'surface') and (0 in plotType):
        plotType.append(2)
    
    congPlotType = [*set(plotType)]
    
    return congPlotType

def RetrievePlots(values, Time):
    
    factors = values['factors'].split(', ')
    
    congPlotType = PullFactors(values)
    
    plotslist = []
    
    for module in amgpmodules:
        var = f"{module}".strip("amgp")
        globals()[f"{var}"] = []
        
        for factor in factors:
            if factor in module.getFactors().keys():
                globals()[f"{var}"].append(factor)
        
        if len(globals()[f"{var}"]) > 0:
            plotslist.extend(module.Retrieve(Time, globals()[f"{var}"], values))
    
    '''
    for factor in factors:
        if factor in amgpobs.getFactors().keys():
            obs.append(factor)
        elif factor in amgpgrd.getFactors().keys():
            grd.append(factor)
        elif factor in amgpsat.getFactors().keys():
            sat.append(factor)
        elif factor in amgpconv.getFactors().keys():
            conv.append(factor)
    
    if len(conv) > 0:
        plotslist.extend(amgpconv.Retrieve(Time, conv))
    if len(obs) > 0:
        plotslist.extend(amgpobs.Retrieve(Time, obs, values))
    if len(grd) > 0:
        plotslist.extend(amgpgrd.Retrieve(Time, grd, values))
    if len(sat) > 0:
        plotslist.extend(amgpsat.Retrieve(Time, sat))
    '''
    
    return plotslist
    
    
# The meat of the program
def run(values, titleOverride, **Override):
    
    setTime()
    
    rewind = 0
    # Handle quickrun overrides
    for k in Override:
        if k == "date":
            values.update({'date':Override[k]})
        if k == "fcHour":
            values.update({'delta':Override[k]})
        if k == "level":
            values.update({'level':Override[k]})
        if k == 'factors':
            values.update({'factors':Override[k]})
        if k == "adtnlRwnd":
            rewind = Override[k]
    
    values.update({'delta':int(values['delta'])})
    
    # Level
    if values['level'] != 'surface':
        level = int(values['level'])
    else:
        level = values['level']
        
    # Date
    Time = amgp.ParseTime(PullFactors(values), values['date'], currentTime, values['timemode'], values['convmode'])
    
    # Panel Preparation
    panel = declarative.MapPanel()
    panel.layout = (1, 1, 1)
    
    # Parse custom zoom feature
    simArea = values['area'].replace("+", "")
    simArea = simArea.replace("-", "")
    if simArea in area_dictionary:
        splitArea = Counter(values['area'])
        factor = (splitArea['+']) - (splitArea['-'])
        scaleFactor = (1 - 2**-factor)/2
        west, east, south, north = area_dictionary[f'{simArea}']
        newWest = west - (west - east) * scaleFactor
        newEast = east + (west - east) * scaleFactor
        newSouth = south - (south - north) * scaleFactor
        newNorth = north + (south - north) * scaleFactor
        modArea = newWest, newEast, newSouth, newNorth
    
        panel.area = modArea
    else:
        panel.area = f'{values["area"]}'

    # Figuring out the data display area
    areaZero = list(panel.area)
    areaScaleA = 1.1
    areaScaleB = 0.9
    if areaZero[0] < 0:
        areaZero[0] = 360 + (areaZero[0] * areaScaleA)
    if areaZero[1] < 0:
        areaZero[1] = 360 + (areaZero[1] * areaScaleB)
    areaZero[2] = areaZero[2] * areaScaleB
    areaZero[3] = areaZero[3] * areaScaleA
    latSlice = slice(areaZero[3], areaZero[2])
    lonSlice = slice(areaZero[0], areaZero[1])
    
    panel.layers = ['states', 'coastline', 'borders']
    
    # Parsing the panel.area into a list, and doing math on it.
    areaList = list(panel.area)
    areaMap = map(int, areaList)
    mapList = list(areaMap)
    diffLat = int(mapList[1])-int(mapList[0])
    diffLon = int(mapList[3])-int(mapList[2])
    avgDiff = ((diffLat + diffLon)//2)
    scaledDiff = math.floor(avgDiff*float(values['scale']))

    # Determining projection
    midLon = (mapList[1]+mapList[0])//2
    midLat = (mapList[3]+mapList[2])//2
    if values['projection'] == '' or values['projection'] == 'custom':
        projection = ccrs.LambertConformal(central_longitude = midLon, central_latitude = midLat)
    elif values['projection'] == 'satelite':
        projection = None
    else:
        projection = values['projection']
    panel.projection = projection
    
    # Data acquisition and packaging
    plotslist = RetrievePlots(values, Time)
    panel.plots = plotslist
    
    # Automatic panel titles
    if titleOverride != '':
        title = titleOverride
        titlebits = str(title)
    else:
        titlebits = []
        plotTypes = PullFactors(values)
        
        if (0 in plotTypes) and (1 not in plotTypes) and (2 not in plotTypes):
            titlebits.append("Obs")
        if (1 in plotTypes) and (2 not in plotTypes):
            titlebits.append("Surface Obs")
        if (1 not in plotTypes) and (2 in plotTypes):
            titlebits.append("Upper-air Obs")
            
        if ((3 in plotTypes) or (6 in plotTypes)) and (4 not in plotTypes) and ((5 not in plotTypes) and (7 not in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Model")
        if (4 in plotTypes) and ((5 not in plotTypes) and (7 not in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Surface Model")
        if (4 not in plotTypes) and ((5 in plotTypes) or (7 in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Upper-air Model")
        
        if 8 in plotTypes:
            titlebits.append("Sat")
        
        if 9 in plotTypes:
            titlebits.append("Day 1 Outlook")
        if 10 in plotTypes:
            titlebits.append("Day 2 Outlook")
        if 11 in plotTypes:
            titlebits.append("Day 3 Outlook")
        if 12 in plotTypes:
            if "day4prob" in values['factors']:
                titlebits.append("Day 4 Probability")
            if "day5prob" in values['factors']:
                titlebits.append("Day 5 Probability")
            if "day6prob" in values['factors']:
                titlebits.append("Day 6 Probability")
            if "day7prob" in values['factors']:
                titlebits.append("Day 7 Probability")
            if "day8prob" in values['factors']:
                titlebits.append("Day 8 Probability")
        
        if Time.category == 'raw':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Raw for Time"
        if Time.category == 'sync':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Synced"
        if (Time.category == 'async-1') or (Time.category == 'async-3') or (Time.category == 'async-6') or (Time.category == 'async-12') or (Time.category == 'async-24'):
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Asyncronous"
        if Time.category == 'near':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Nearest per Item"
    
    panel.left_title = f"AMGP v{version}"
    panel.title = f"{values['area']} - {title}"
    if level == 'surface':
        panel.right_title = "Surface"
    else:
        panel.right_title = f"{level}mb"
    
    panel.title_fontsize = (scaledDiff**0.75) * 1.5
                            
    return {'panelSize':(scaledDiff, scaledDiff),'panel':panel,'timeObj':Time,'values':values, 'titlebits':titlebits}
    
    
def SaveMap(product, doSave, noShow):
    
    daystamp = product['timeObj'].ds
    timestampNum = product['timeObj'].tsnum
    timestampAlp = product['timeObj'].tsalp
    cat = product['timeObj'].category
    
    nowstamp = amgp.ParseTime([-1], "recent", currentTime, "raw", "latest").tsfull
    
    pc = declarative.PanelContainer()
    pc.size = product['panelSize']
    pc.panels = [product['panel']]
    
    # Saving the map
    OldDir = os.path.isdir(f'Maps/{daystamp}')
    
    if type(product['titlebits']) == str:
        inst = product['titlebits']
    elif type(product['titlebits']) == list:
        inst = ', '.join(product['titlebits'])

    if doSave:
        if OldDir == False:
            os.mkdir(f'Maps/{daystamp}')
        pc.save(f"Maps/{daystamp}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
        save = Image.open(f"Maps/{daystamp}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
        if noShow == False:
            save.show()
        print("<run> Map successfully saved!")
    else:
        if os.path.isdir("Maps/Temp") == False:
            os.mkdir("Maps/Temp")
        pc.save(f"Maps/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
        save = Image.open(f'Maps/Temp/Temp.png')
        save.show()


# --- End Definitions ---



# Init
area_dictionary = dict(config['areas'])
area_dictionary = {k: tuple(map(float, v.split(", "))) for k, v in area_dictionary.items()}

global quickRun
global noShow
quickRun = False
noShow = False

# Check for quickrun commands

if len(sys.argv) > 1:
    sys.exit()
else:
    # Version handler
    print(f"<menu> You are using AMGP version {version}")
    cfgver = config["config_ver"].split('.')
    amgpver = version.split('.')
    if config["config_ver"] != version:
        if cfgver[0] > amgpver[0]:
            sys.exit(f"<error> Your installed AMGP version is out of date! Config version {config['config_ver']} found.")
        elif cfgver[0] < amgpver[0]:
            sys.exit(f"<error> The config we found is out of date! Config version {config['config_ver']} found.")
            # attempt to update the config in the future
        elif cfgver[1] > amgpver[1]:
            sys.exit(f"<error> Your installed AMGP version is out of date! Config version {config['config_ver']} found.")
        elif cfgver[1] < amgpver[1]:
            print(f"<warning> The loaded config file is of an earlier version ({config['config_ver']}), consider updating it.")
        else:
            print(f"<warning> The loaded config file we found is of a different compatible version version ({config['config_ver']}).")
    print("<menu> Config loaded.")
    
    print(f"<menu> Loaded AMGP modules: {amgpmodulenames}")

    # Pre-running
    getTime()
    presetLoad('default')
    setInit()
    singleLoads()

    inputChain()