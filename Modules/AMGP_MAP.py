################################################
#                                              #
#       Automated Map Generation Program       #
#           Map Generation Module              #
#            Author: Sam Bailey                #
#        Last Revised: Apr 12, 2023            #
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

from Modules import AMGP_UTIL as amgp

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_MAP",
            'priority':-2,
            'type':0}
                
def PullFactors(values, amgpmodules):
    
    factorList = values['factors'].split(', ')
    
    plotType = []
    
    for factor in factorList:
        for module in amgpmodules.values():
            if factor in module.getFactors().keys():
                plotType.append(module.getFactors()[f'{factor}'])
                
    if (values['level'] == 'surface') and (0 in plotType):
        plotType.append(1)
    if (values['level'] != 'surface') and (0 in plotType):
        plotType.append(2)
    
    congPlotType = [*set(plotType)]
    
    return congPlotType

def RetrievePlots(values, Time, amgpmodules):
    
    factors = values['factors'].split(', ')
    
    congPlotType = PullFactors(values, amgpmodules)
    
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
def Panel(Time, plotslist, values, area_dictionary, amgpmodules, titleOverride, S, noShow, version):
    
    # Panel Preparation
    panel = declarative.MapPanel()
    panel.layout = (1, 1, 1)
    level = values['level']
    
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
    panel.plots = plotslist
    
    # Automatic panel titles
    if titleOverride != '':
        title = titleOverride
        titlebits = str(title)
    else:
        titlebits = []
        plotTypes = PullFactors(values, amgpmodules)
        
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
    
def SaveMap(product, doSave, noShow, version):
    
    daystamp = product['timeObj'].ds
    timestampNum = product['timeObj'].tsnum
    timestampAlp = product['timeObj'].tsalp
    cat = product['timeObj'].category
    currentTime = product['timeObj'].now
    
    nowstamp = amgp.ParseTime([-1], "recent", currentTime, "raw", "latest").tsfull
    
    pc = declarative.PanelContainer()
    pc.size = product['panelSize']
    pc.panels = [product['panel']]
    
    # Saving the map
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
    OldDir = os.path.isdir(f'{dr}/{daystamp}')
    
    if type(product['titlebits']) == str:
        inst = product['titlebits']
    elif type(product['titlebits']) == list:
        inst = ', '.join(product['titlebits'])

    if doSave:
        if OldDir == False:
            os.mkdir(f'{dr}/{daystamp}')
        pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
        save = PImage.open(f"{dr}/Temp/Temp.png").convert('RGBA')
        save = amgp.Watermark(save, version)
        save.save(f"{dr}/{daystamp}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
        if noShow == False:
            save.show()
        print("<run> Map successfully saved!")
    else:
        if os.path.isdir(f"{dr}/Temp") == False:
            os.mkdir(f"{dr}/Temp")
        pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
        save = PImage.open(f'{dr}/Temp/Temp.png').convert('RGBA')
        save = amgp.Watermark(save, version)
        save.show()


# --- End Definitions ---