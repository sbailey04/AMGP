################################################
#                                              #
#       Automated Map Generation Program       #
#               Plotting Module                #
#            Author: Sam Bailey                #
#        Last Revised: May 09, 2023            #
#                Version 0.3.0                 #
#             AMGP Version: 0.3.0              #
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
from PIL import Image as PImage
from PIL import ImageDraw, ImageFont, ImageFilter
import json
import glob
import contextlib
from importlib import import_module

from tkinter import *
from tkinter import ttk

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)

#----------------- AMGP IMPORTS -------------------#

from Modules import AMGP_MAP as amgpmap
from Modules import AMGP_UTIL as amgp

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_PLT",
            'uid':"00220100"}

def init(pack):
    print("<menu_init> Opened the singular plotting interface <menu_init>")
    global unpack
    global area_dictionary
    global version
    global amgpmodules
    global noShow
    global amgpmenumodules
    global amgpcombomodules
    global modules
    noShow = False
    unpack = pack
    config = unpack['config']
    area_dictionary = unpack['customareas']
    version = unpack['ver']
    modules = unpack['modulenames']
    amgpmodules = unpack['datamods']
    amgpmenumodules = unpack['menumods']
    amgpcombomodules = unpack['combomods']
    imports(unpack)
    amgp.getTime()
    setInit()
    presetLoad('default')
    singleLoads()
    inputChain()
    
def imports(unpack):
    for module in unpack['datamods'].values():
        import_module(module.__name__)

# Definitions
def inputChain():
    amgp.ClearTemp()
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
        currentTime = amgp.getTime()
        inputChain()
#    elif command[0] == 'update':
#        cfgUpdate()
#        inputChain()
    elif command[0] == 'preset':
        if command[1] == 'list':
            plotkeys = []
            for item in unpack['presets']:
                spi = item[0].split("-")
                if spi[0] == "plot":
                    plotkeys.append(spi[1])
            print("<presets> Below is the list of all currently loaded presets:")
            for item in plotkeys:
                print(f"<presets> (obs) {item}")
            inputChain()
        else:
            presetLoad(command[1])
            singleLoads()
            inputChain()
    elif command[0] == 'factors':
        for module in amgpmodules.values():
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
                    try:
                        loaded.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}, {command[6]}'})
                    except:
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
        Time, plotslist, values = run(loaded, amgpmodules)
        amgpmap.SaveMap(amgpmap.Panel(Time, plotslist, values, area_dictionary, amgpmodules, title, version), S, noShow)
        inputChain()
    elif command[0] == 'switch':
        try:
            y = command[1]
        except:
            print("<error> Please enter a module name to switch to.")
            inputChain()
        if (f'AMGP_{command[1].upper()}' in modules.values()) or (f'AMGP_{command[1].upper()}' in modules.values()):
            for k, v in modules.items():
                if ((k in amgpmenumodules.keys()) or (k in amgpcombomodules.keys())) and (f'AMGP_{command[1].upper()}' == v):
                    try:
                        newMod = amgpmenumodules[k]
                    except:
                        newMod = amgpcombomodules[k]
                    newMod.init(unpack)
                    break
        print("<error> That is not a valid module to switch to!")
        inputChain()
           
    elif command[0] == 'quit':
        sys.exit("<quit> The process was terminated.")
    else:
        print("<error> That is not a valid command!")
        inputChain()
        
#      ------ End inputChain() ------
        
# Save an obs preset
def save(name):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    saveState = {"level":f"{loaded['level']}","date":f"{loaded['date']}","delta":f"{loaded['delta']}","factors":f"{loaded['factors']}","area":f"{loaded['area']}","dpi":f"{loaded['dpi']}","scale":f"{loaded['scale']}","prfactor":f"{loaded['prfactor']}","barbfactor":f"{loaded['barbfactor']}","smoothing":f"{loaded['smoothing']}","projection":f"{loaded['projection']}","timemode":f"{loaded['timemode']}","convmode":f"{loaded['convmode']}"}
    data = {"amgp_ver":version,"type":"obs","settings":saveState}
    
    if os.path.isfile(f"{dr}/plot/{name}.json"):
        os.remove(f"{dr}/plot/{name}.json")
    
    with open(f"{dr}/plot/{name}.json", "a") as J:
        json.dump(data, J)

# Load a preset from the config file
def presetLoad(loadedPreset):
    global loaded
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    with open(f"{dr}/plot/{loadedPreset}.json", "r") as J:
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
                
def PullFactors(values, amgpmodules):
    
    factorList = values['factors'].split(', ')
    
    plotType = []
    fillType = []
    
    for factor in factorList:
        for module in amgpmodules.values():
            if factor in module.getFactors().keys():
                plotType.append(module.getFactors()[f'{factor}'][0])
                fillType.append(module.getFactors()[f'{factor}'][1])
                
    if (values['level'] == 'surface') and (0 in plotType):
        plotType.append(1)
    if (values['level'] != 'surface') and (0 in plotType):
        plotType.append(2)
    
    congPlotType = [*set(plotType)]
    congFillType = [*set(fillType)]
    
    return [congPlotType, congFillType]

def RetrievePlots(values, Time, amgpmodules):
    
    factors = values['factors'].split(', ')
    
    congPlotType = PullFactors(values, amgpmodules)[0]
    
    plotslist = []
    
    for module in amgpmodules.values():
        var = f"{module}".strip("amgp")
        globals()[f"{var}"] = []
        
        for factor in factors:
            if factor in module.getFactors().keys():
                globals()[f"{var}"].append(factor)
        
        if len(globals()[f"{var}"]) > 0:
            plotslist.extend(module.Retrieve(Time, globals()[f"{var}"], values))
    
    return plotslist
    
    
# The meat of the program
def run(values, amgpmodules, **Override):
    
    currentTime = amgp.setTime()
    
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
    level = amgp.GetLevel(values['level']).level
    values['level'] = level
        
    # Date
    Time = amgp.ParseTime(values['date'], PullFactors(values, amgpmodules)[0], currentTime, values['timemode'], values['convmode'])
    
    # Data
    plotslist = RetrievePlots(values, Time, amgpmodules)
    
    return Time, plotslist, values


# --- End Definitions ---