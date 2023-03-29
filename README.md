# AMGP - The Automated Map Generation Program
Copyright (c) 2023, Samuel Nelson Bailey
  
The Automated Map Generation Program is a Python-core program used to produce a variety of customizable meteorological maps, originally based on my freshman coursework. It allows users to use raw data from a variety of sources in the backend of the program, automatically compiling them and saving them as high-definition images. With a variety of interchangeable modules to handle the program's many mapping capabilities, adding and editing functionality to your own version is as simple as learning Python and finding your data.

## Raw Python Usage
If you download the source code, you can run:
```
python AMGP/AMGP.py
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
"<startup> AMGP_* loaded as amgp*"
# Any code references within AMGP will refer to the lowercase version of the module name, without the underscore.

# Your module must import AMGP_UTIL, as the content of the utilities module is vital to everything AMGP does.
from Modules import AMGP_UTIL as amgp

# Your module must have the following:
def getFactors():
  return {
          key : value # where the key is the name of the factor to plot and value is the timecode as defined below, for each factor
         }

def factors():
  print("<factors_{module name}> '{factor name}' - {factor description}") # for each factor

# Time is a Time object (which contains many datetime objects, refer to the UTIL module)
# factors are any factors that AMGP automatically detected from the input, found in your module's getFactors()
# values are the full set of input conditions given when the program was run
def Retrieve(Time: Time, list: factors, dict: values):
  # Whatever the heck the module does.
  return partialPlotsList # appends to panel.plots as a return. In the future, there will be the option to have modules that DON'T depend on this function
~~~
