from win32api import GetSystemMetrics
import comtypes

# Start new instance of STK
from comtypes.client import CreateObject
uiApplication = CreateObject('STK11.Application')
uiApplication.Visible = True

# Alternatively, uncomment the following lines to get a reference to a running STK instance
# from comtypes.client import GetActiveObject
# uiApplication=GetActiveObject('STK11.Application')
# uiApplication.Visible=True

# Get our IAgStkObjectRoot interface
root=uiApplication.Personality2

#Note: When 'root=uiApplication.Personality2' is executed, the comtypes library automatically creates a gen folder that contains STKUtil and STK Objects. After running this at least once on your computer, the following two lines should be moved before the 'uiApplication=CreateObject("STK11.Application")' line for improved performance.

from comtypes.gen import STKUtil
from comtypes.gen import STKObjects