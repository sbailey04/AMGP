################################################
#                                              #
#       Automated Map Generation Program       #
#                                              #
#            Author: Sam Bailey                #
#        Last Revised: Apr 12, 2023            #
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

try:
    from Modules import AMGP_UTIL as amgp
    print("<startup> AMGP_UTIL imported as amgp")
except:
    sys.exit("<error> AMGP cannot function without the Utilities module.")

try:
    from Modules import AMGP_MAP as amgpmap
    print("<startup> AMGP_MAP imported as amgpmap")
except:
    sys.exit("<error> AMGP cannot function without the Mapping module.")

try:
    from Modules import AMGP_PLT as amgpplt
    print("<startup> AMGP_PLT imported as amgpplt")
except:
    sys.exit("<error> AMGP cannot function without the Plotting module.")

amgputilmodules = {}
amgpmodules = {}
amgpmenumodules = {}
amgpcombomodules = {}

amgpmodulenames = {-3:"AMGP_PLT",-2:"AMGP_MAP",-1:"AMGP_UTIL"}

for module in os.listdir("Modules"):
    if module.startswith("AMGP_") and (module.replace(".py","") not in amgpmodulenames.values()):
        strp = module.replace(".py", '')
        var = strp.replace("_", '').lower()
        globals()[f"{var}"] = import_module(f'Modules.{strp}')
        print(f"<startup> {strp} imported as {var}")
        tmp = globals()[f"{var}"].info()
        if tmp['type'] == 0:
            amgputilmodules[tmp['priority']] = globals()[f"{var}"]
            amgputilmodules = dict(sorted(amgputilmodules.items()))
        elif tmp['type'] == 1:
            amgpmodules[tmp['priority']] = globals()[f"{var}"]
            amgpmodules = dict(sorted(amgpmodules.items()))
        elif tmp['type'] == 2:
            amgpmenumodules[tmp['priority']] = globals()[f"{var}"]
            amgpmenumodules = dict(sorted(amgpmenumodules.items()))
        elif tmp['type'] == 3:
            amgpcombomodules[tmp['priority']] = globals()[f"{var}"]
            amgpcombomodules = dict(sorted(amgpcombomodules.items()))
        amgpmodulenames[tmp['priority']] = f"{strp}"

amgpmodulenames = dict(sorted(amgpmodulenames.items()))

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

# Init
area_dictionary = dict(config['areas'])
area_dictionary = {k: tuple(map(float, v.split(", "))) for k, v in area_dictionary.items()}

if len(sys.argv) > 1:
    sys.exit()
else:
    print(f"<menu> Loaded AMGP modules: {list(amgpmodulenames.values())}")
    
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

    # Packing and starting the program
    
    pack = {'modulenames':amgpmodulenames,
            'utilmods':amgputilmodules,
            'datamods':amgpmodules,
            'menumods':amgpmenumodules,
            'combomods':amgpcombomodules,
            'customareas':area_dictionary,
            'ver':version,
            'presets':presets,
            'config':config}
    
    amgpplt.init(pack)