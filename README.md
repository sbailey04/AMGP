# AMGP - The Automated Map Generation Program
Copyright (c) 2023-2024, Samuel Nelson Bailey
  
The Automated Map Generation Program is a Python-core program used to produce a variety of customizable meteorological maps, originally based on my freshman coursework. It allows users to use raw data from a variety of sources in the backend of the program, automatically compiling them and saving them as high-definition images. With a variety of interchangeable modules to handle the program's many mapping capabilities, adding and editing functionality to your own version is as simple as learning Python and finding your data.

## Raw Python Usage
If you download the source code, you can run:
```
python AMGP/Main.py
```
from your terminal.

You'll be prompted via your terminal to edit the parameters to create maps, which will be saved to AMGP/Maps/{%Y%m%d}.

## Creating Custom Modules
If you want to create your own modules for AMGP, the things to keep in mind are as follows:

~~~python
# Your module must be named
"AMGP_*.py"
# Where * is the name of your module.
# Upon starting AMGP, with your module in "AMGP/Modules" you should be greeted by a message stating
"(AMGP_Main) <startup> AMGP_* loaded as amgp*"
# Any code references within AMGP will refer to the lowercase version of the module name, without the underscore.

# Your module must import AMGP_UTIL, as the content of the utilities module is vital to everything AMGP does.
from Modules import AMGP_UTIL as amgp

# Your module must have the following:
def info():
  return {
          "name" : str(module_name) # module_name is equivalent to AMGP_*
          "uid" : str(id) # the id is a unique identifier for the module, consisting of 8 digits stored in
                          # string form. The first three digits denote the module number, the fourth digit
                          # denotes module type, and the last four denote module priority.
          # priority dictates when the module is ordered among other modules (for data modules,
          # this dictates map layer plotting order), with higher modules plotted below lower modules
          # module type tells AMGP how this module should be treated. 0 is a utility module, 1 is a data
          # acquisition module, 2 is an input loop, 3 combines data acquisition and input loops
         }


# A module of type 1 must also have:
def getFactors():
  return {
          str(factor_name) : [int(timecode), int(fill)] # where factor_name is the name of the factor to plot,
                                                        # the timecode as defined below, and a boolean 0 or 1
                                                        # denoting whether or not the factor being plotted applies
                                                        # color to whole of the map; these must be defined within
                                                        # this dictionary for each factor
         }

def factors():
  print("(AMGP_{uppercase module name}) <factors_{module name}> '{factor name}' - {factor description}")
  # for each factor

# Modules, whether they import data or not, must have the below function.
# The below is just an example for how I handle it. If your module imports no data,
# simply return within the ping() function.
def ping(Time: Time):
  try:
    with urlopen("{data source}", timeout=3) as conn:
      print("(AMGP_{uppercase module name}) <ping> {affirmative message}")
  except:
    print("(AMGP_{uppercase module name}) <ping> {negative message}")
# This try-except is used for ever imported data source that AMGP directly sources, as both a method of displaying
# data sources, and testing whether or not a give source is online.

# Time is a Time object (which contains many datetime objects, refer to the UTIL module)
# factors are any factors that AMGP automatically detected from the input, found in your module's getFactors()
# values are the full set of input conditions given when the program was run
def Retrieve(Time: Time, list: factors, dict: values):
  # Whatever the module does.
  return partialPlotsList # appends to panel.plots as a return.


# A module of type 2 or 3 must also have:

def init():
  # What you actually need to do within this function is up to how your module will function,
  # but you should call your input loop within it.
  # Your input loop should also be able to import the base modules - specifically AMGP_PLT -
  # and be able to call the init() function within it, otherwise there will be no easy way to
  # return to the base of the program
~~~
