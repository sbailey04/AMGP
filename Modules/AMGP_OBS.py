################################################
#                                              #
#       Automated Map Generation Program       #
#          Base Observation Module             #
#            Author: Sam Bailey                #
#        Last Revised: Apr 12, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
from io import StringIO
from urllib.request import urlopen
from siphon.simplewebservice.iastate import IAStateUpperAir
from siphon.catalog import TDSCatalog

from metpy.io import add_station_lat_lon
from metpy.io import metar
from metpy.plots import declarative
from metpy.units import units
import os
import pandas as pd
import sys

from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_OBS",
            'priority':1,
            'type':1}

def getFactors():
    return {'temperature':0,
            'dewpoint':0,
            'dewpoint_depression':0,
            'height':2,
            'pressure':1,
            'current_weather':1,
            'barbs':0,
            'cloud_coverage':1}

def factors():
    print("<factors_obs> 'temperature' - Observation station temps")
    print("<factors_obs> 'dewpoint' - Observation station dewpoints")
    print("<factors_obs> 'dewpoint_depression' - Observation station dewpoint depressions")
    print("<factors_obs> 'height' - Observation station pressure heights (upper-air only)")
    print("<factors_obs> 'pressure' - Observation station pressures (surface only)")
    print("<factors_obs> 'current_weather' - Observation station weather (surface only)")
    print("<factors_obs> 'barbs' - Observation station wind")
    print("<factors_obs> 'cloud_coverage' - Observation station cloud coverage (surface only)")

def Retrieve(Time, factors, values):
    
    partialPlotsList = []
    
    LVL = amgp.GetLevel(values['level'])
    
    level = LVL.level
    
    # Pulling the surface data
    Data = FetchData(Time, level)
    
    # Level-based formatting
    
    if LVL.level != "surface":
        steps = LVL.steps
        height_format = LVL.height_format
    mslp_formatter = LVL.mslp_formatter
    
    obsfields = []
    obscolors = []
    obslocations = []
    obsformats = []
    
    obs = declarative.PlotObs()
    if level == 'surface':
        obs.data = Data.sfcDat
    else:
        obs.data = Data.uaDat
    
    if obs.data is None:
        print("<error> You cannot make a map using factors that would cause obs data to attempt and fail a pull.")
        amgpplt.inputChain()
    
    try:
        obs.time = Time.time
    except AttributeError:
        if level == 'surface':
            obs.time = Time.threetime
        else:
            obs.time = Time.twelvetime

    if "temperature" in factors:
        if level == 'surface':
            obsfields.append('tmpf')
        else:
            obsfields.append('temperature')
        obscolors.append('crimson')
        obslocations.append('NW')
        obsformats.append(None)
    if "dewpoint" in factors:
        if level == 'surface':
            obsfields.append('dwpf')
        else:
            obsfields.append('dewpoint')
        obscolors.append('green')
        obslocations.append('SW')
        obsformats.append(None)
    elif "dewpoint_depression" in factors:
        obsfields.append('dewpoint_depression')
        obscolors.append('green')
        obslocations.append('SW')
        obsformats.append(None) # height_format?
    if "height" in factors:
        obsfields.append('height')
        obscolors.append('darkslategrey')
        obslocations.append('NE')
        obsformats.append(height_format)
    if "pressure" in factors:
        obsfields.append('air_pressure_at_sea_level')
        obscolors.append('darkslategrey')
        obslocations.append('NE')
        obsformats.append(mslp_formatter)
    if 'current_weather' in factors:
        obsfields.append(f'{Data.weather_format}')
        obscolors.append('indigo')
        obslocations.append('W')
        obsformats.append('current_weather')
    if "barbs" in factors:
        if level == 'surface':
            obs.vector_field = ['eastward_wind', 'northward_wind']
        else:
            obs.vector_field = ['u_wind', 'v_wind']
    if "cloud_coverage" in factors:
        obsfields.append('cloud_coverage')
        obscolors.append('black')
        obslocations.append('C')
        obsformats.append('sky_cover')


    obs.fields = obsfields
    obs.colors = obscolors
    obs.formats = obsformats
    obs.locations = obslocations
    obs.reduce_points = float(values['prfactor'])

    if level == 'surface':
        obs.level = None
        obs.time_window = timedelta(minutes=15)
    else:
        obs.level = level * units.hPa
        
    partialPlotsList.append(obs)
    
    return partialPlotsList

class Data(object):
    def __init__(self, Time, level):
        
        if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
            timesfc = Time.time
            timeua = Time.time
        else:
            timesfc = Time.threetime
            timeua = Time.twelvetime
        
        if level == 'surface':
            if timesfc.year < 2019:
                try:
                    self.sfcDat = pd.read_csv(f'http://bergeron.valpo.edu/archive_surface_data/{timesfc:%Y}/{timesfc:%Y%m%d}_metar.csv', parse_dates=['date_time'], na_values=[-9999], low_memory=False)
                    self.weather_format = 'present_weather'
                    self.sfcDat['tmpf'] = (self.sfcDat.air_temperature.values * units.degC).to('degF')
                    self.sfcDat['dwpf'] = (self.sfcDat.dew_point_temperature.values * units.degC).to('degF')
                except:
                    print("<warning> Archive surface obs not found!")
                    self.sfcDat = None
            elif Time.recentness < timedelta(days=14):
                try:
                    data = StringIO(urlopen('http://bergeron.valpo.edu/current_surface_data/'f'{timesfc:%Y%m%d%H}_sao.wmo').read().decode('utf-8', 'backslashreplace'))
                    self.sfcDat = metar.parse_metar_file(data, year=timesfc.year, month=timesfc.month)
                    self.sfcDat['tmpf'] = (self.sfcDat.air_temperature.values * units.degC).to('degF')
                    self.sfcDat['dwpf'] = (self.sfcDat.dew_point_temperature.values * units.degC).to('degF')
                    self.weather_format = 'current_wx1_symbol'
                except:
                    print("<warning> Recent surface obs not found!")
                    self.sfcDat = None
            else:
                print("<warning> The date you have selected is not in range for surace obs!")
                self.sfcDat = None
            
        
        if level != 'surface':
            try:
                self.uaDat = IAStateUpperAir.request_all_data(timeua)
                self.uaDat = add_station_lat_lon(self.uaDat, 'station').dropna(subset=['latitude', 'longitude'])
                self.uaDat = self.uaDat[self.uaDat.station != 'KVER'] # "central Missouri" station that shouldn't be there, due to faulty lat-lon data
                self.uaDat['dewpoint_depression'] = self.uaDat['temperature'] - self.uaDat['dewpoint']
            except:
                print("<warning> The date you have selected has no upper-air data available!")
                self.uaDat = None

def FetchData(Time, level):
    return Data(Time, level)