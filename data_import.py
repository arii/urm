import re
import pandas as pd
import seaborn as sns
from numpy import median
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager as fm, rcParams
import glob

USE_STORED = True

arankcodes = pd.read_csv("arankcodes.csv")
racecodes = pd.read_csv("racecodes.csv")
carnegie = pd.read_csv("carnegieclassification.csv")

def create_dict(df, x, y):
    return dict(zip(df[x], df[y]))

unidict = create_dict(carnegie, 'unitid', 'name')
ratingdict = create_dict(carnegie, 'unitid', 'rating')
racedict = create_dict(racecodes, 'code', 'combined_race')

#urmlist = "black grand".split(" ") #urmlist = "black indian hispanic grand".split(" ")
#urmcheck = lambda x : any( u in x for u in urmlist)
#urmcodes = [c for (c,r) in zip(racecodes['code'], racecodes['race']) if urmcheck(r.lower())]
#racecolumns = urmcodes  
racecolumns = list(racecodes['code'])

COLUMNS = ["YEAR", "UNITID", "ARANK"] + racecolumns 

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


def arankToInstructor(df):
    eng_df = df.copy()

    combined_year_dicts = {}
    for y in arankcodes['year'].unique():
        combined_year_dicts[y] = create_dict(arankcodes[arankcodes['year'] == y], 'code', 'title')
    year_dicts = {}
    for key in combined_year_dicts:
        for y in key.split():
            year_dicts[y] = combined_year_dicts[key]
    eng_df["INSTRUCTOR"] = [""]*len(eng_df)
    for year in df.YEAR.unique():
        if year in year_dicts:
            instdict = year_dicts[year]
            idx = eng_df["YEAR"] == year

            eng_df.loc[idx, ["INSTRUCTOR"]] = eng_df[idx]["ARANK"].replace(instdict)

        
    return eng_df

def dfToEnglish(df):
    new_df = df.copy() # df[df.UNITID.isin(unidict)].copy()
    new_df['NAME'] = new_df.UNITID.replace(unidict)
    new_df['RANK'] = new_df.UNITID.replace(ratingdict)
    new_df = arankToInstructor(new_df)
    return new_df



def readAllData():
    csv_dataframes = []
    for i, f in enumerate(glob.glob("iped/*csv")):
        if "rv" in f : continue # remove all revised stuff
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

DF = getDataFrame()
eng_df = dfToEnglish(DF)
eng_df = eng_df.drop(columns=["ARANK", "UNITID"])
new_columns  = ["YEAR", "NAME", "RANK", "INSTRUCTOR"] 
eng_df = eng_df.melt(new_columns,var_name="race gender") 
eng_df['race gender']  = eng_df['race gender'].replace(racedict)

gb = eng_df.groupby(["YEAR","race gender"]).sum() 
gb = gb.unstack("YEAR")

eng_df.to_csv("full_data.csv")
gb.to_csv("grouped_data.csv")
