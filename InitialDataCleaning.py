# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 11:39:54 2024

@author: alexi
"""

import pandas as pd
import numpy as np

# Read in ititial data and remove unused variables
# Initial Data: 1% sample of individuals from 1900,1910,1920,1930,1940,and 1950 U.S. censuses with consistant variables for:
#   - geography (state,state economic area (SEA), and county)
#   - demographic variables (sex, age, race, hispanic status, marital status, and birthplace)
raw_data = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/usa_00012.csv/usa_00012.csv")
raw_data.drop(["SAMPLE","SERIAL","HHWT", "CLUSTER","REGION", "CITY", "STRATA", "CNTRY", "PERNUM", "PERWT",
               "RACED", "HISPAND", "BPLD"], axis=1, inplace=True)

# Centroid latitudes and longitudes found using 'calculate geometry attributes' tool on polygons in ArcGIS Pro.
# (uses 1940 boundaries, which are fairly consistant with between 1900-1950)

# Combine with state centroid lat and lon
state_coordinates = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/states_latlon.csv")
df = pd.merge(state_coordinates,raw_data,on="STATEICP")
df['County'] = df['STATEICP'].astype(str) +"_"+ df['COUNTYICP'].astype(str)
df = pd.DataFrame(df)

# Combine with county centroid lat and lon
county_coordinates = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/county_latlon.csv")
county_coordinates['County'] = county_coordinates['STATEICP'].astype(str) +"_"+ county_coordinates['COUNTYICP'].astype(str)
county_coordinates.drop(["COUNTYICP","STATEICP"], axis=1, inplace=True)
df = pd.merge(county_coordinates,df,on="County")

# Combine with sea centroid lat and lon
sea_coordinates = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/sea_latlon.csv")
df = pd.merge(sea_coordinates,df,on="SEA")

# Restrict to Contiguious U.S. by removing individuals from Alaska and Hawaii 
# (Not states at the time and missing alot of data)
df = df[(df['state_abv'] != "AK") & (df['state_abv'] != "HI")]

#county_agg = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/county_aggregated.csv")
#sea_agg = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/sea_aggregated.csv")
#state_agg = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/state_aggregated.csv")

# Simplify birthplace to within U.S. (1) and outside U.S. (0)
# (Birthplace originally has hundreds of observations for specific states and countries)
df["BPL"] = np.where(df["BPL"] <= 99, 1, 0)

# Replace numbered demogrpahic variable responses with meaningful responses
df["RACE"] = df["RACE"].replace({
    1: "White",
    2: "Black/African American",
    3: "Native American",
    4: "Chinese",
    5: "Japanese",
    6: "Other Asian or Pacific Islander",
    7: "Other Race"
    })
df["MARST"] = df["MARST"].replace({
    1: "Married, spouse present",
    2: "Married, spouse absent",
    4: "Divorced",
    5: "Widowed",
    6: "Never married/single"
    })
df["HISPAN"] = df["HISPAN"].replace({
    0: "Not Hispanic",
    1: "Mexican",
    2: "Puerto Rican",
    3: "Cuban",
    4: "Other Hispanic"
    })

# Export cleaned data
df.to_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/usa_00012_CLEANED_final.csv", index=False)

