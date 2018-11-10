import re
import pandas as pd
import seaborn as sns
from numpy import median
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager as fm, rcParams
import glob

USE_STORED = not True

arankcodes = pd.read_csv("arankcodes.csv")
racecodes = pd.read_csv("racecodes.csv")
carnegie = pd.read_csv("carnegieclassification.csv")
unidict = dict(zip(carnegie['unitid'], carnegie['name']))
ratingdict = dict(zip(carnegie['unitid'], carnegie['rating']))
racedict = dict(zip(racecodes['code'], racecodes['race'])) 

urmlist = "black grand".split(" ") #urmlist = "black indian hispanic grand".split(" ")
urmcheck = lambda x : any( u in x for u in urmlist)
urmcodes = [c for (c,r) in zip(racecodes['code'], racecodes['race']) if urmcheck(r.lower())]
COLUMNS = ["YEAR", "UNITID", "ARANK"] + urmcodes # list(racecodes["code"])
other =    "Other Faculty"
associate =  "Associate Professor"
assistant = "Assistant Professor"
full = "Full Professor"

def getRaceGender(code):
    """ this function returns the race and gender group given a code
    assert getRaceGender('HRNRALT') == "Nonresident alien total"
    """
    group = racecodes[racecodes["code"]==code]['race'].iloc[0]
    return group

def getARANK((year, code)):
    """
    this function takes a year and ARANK code as input.  It returns Full Professor, Associate Professor, Assistant Professor, or Other Faculty"
    assert getARANK(2012,2) == "Associate Professor"
    """
    year_idx = arankcodes['year'].str.contains(str(year))
    if len(year_idx) == 0: 
        print "ARANK year %s is not found in database" %  year
        return other
    code_idx = arankcodes['code'] == code
    if len(code_idx) == 0:
        print "ARANK code %s is not found in database" % code
        return other
    title = arankcodes[(year_idx & code_idx)]['title']
    if len(title) == 0:
        print "ARANK with Year %s and code %s is not found" % (year, code)
        return other
    rank =  title.iloc[0].lower()
    if "professor" in rank:
        if "associate" in rank:
            return associate
        elif "assistant" in rank: 
            return assistant
        else:
            return full
    else:
        return  other

def dfToEnglish(df):
    new_df = df[ df.UNITID.isin(unidict)]
    new_df = new_df.rename(columns=racedict)
    new_df['NAME'] = list(new_df.UNITID)
    new_df['RANK'] = list(new_df.UNITID)
    new_df['NAME'] = new_df.NAME.replace(unidict)
    new_df['RANK'] = new_df.RANK.replace(ratingdict)

    yrdf = new_df[["YEAR", "ARANK"]] 
    ranks = [getARANK(row) for idx,row in yrdf.iterrows()]
    new_df["INSTRUCTOR"] = ranks

    return new_df



def readAllData():
    csv_dataframes = []
    for i, f in enumerate(glob.glob("iped/*csv")):
        try:
            year = re.findall(r'\d+', f)
            assert len(year) == 1
            year = year[0]
            df = pd.read_csv(f)

        except:
            print "could not read csv file %s" % f
            continue

        
        dlen= len(df)
        for col in COLUMNS:
            if col == "YEAR": continue
            if not col in df:
                df[col] = [0]*dlen
        df['YEAR'] = [year]*dlen
        csv_dataframes.append( df[COLUMNS])
        print "successfully loaded %s" % f
        #if i > 0: break
    if len(csv_dataframes) == 0:
        print "No csv files loaded"
        return None
    df = pd.concat(csv_dataframes)
    
    return df

def getDataFrame():
    alldataname = "dataframe.h5"
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
eng_df = dfToEnglish(df)
eng_df.to_csv("blackcomp.csv")

