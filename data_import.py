import pandas as pd
import seaborn as sns
from numpy import median
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager as fm, rcParams
import glob

USE_STORED = True

def readAllData():
    csv_dataframes = []
    for f in glob.glob("iped/*csv"):
        try:
            df = pd.read_csv(f)
            csv_dataframes.append(df)
            print "successfully loaded %s" % f
        except:
            print "could not read csv file %s" % f
        break
    if len(csv_dataframes) == 0:
        print "No csv files loaded"
        return None
    return csv_dataframes

    return None
    
def getDataFrame():
    alldataname = "dataframe.pl"
    dataframe = None
    if USE_STORED:
        try:
            dataframe = pd.read_hdf(alldataname, 'df')
            print "dataframe loaded"
        except:
            print "could not load stored data frame %s " % alldataname

    if dataframe is None:
        dataframe = readAllData()
        dataframe.to_hdf(alldataname,'df')
        print "saved all data to %s " % alldataname
    return dataframe

df = getDataFrame()
#dataframe = pd.DataFrame(data=datavalues, columns=datakeys)

