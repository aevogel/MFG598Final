# -*- coding: utf-8 -*-
"""
MFG598 Final Project:

Interactive Map that displays U.S. Census Data

@author: alexi
"""
import streamlit as st
import pandas as pd
import numpy as np
#import folium
from streamlit_folium import st_folium
import statistics
import gc
import json


st.title("Interactive Mapping with Census Data")
st.write("MFG598 Final Project - Alexi Vogel")
st.write("Summary: Interactive map that displays summary tables of U.S. Decennial Census data from 1900 to 1950, for multiple levels of aggregation and variables.")
st.write("")

#gc.enable()

# Read in Cleaned Data
df = pd.read_csv("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/usa_00012_CLEANED_final.csv")
df["County"] = df["County"].astype(str)

# Change Census Year - 1900 to 1950
year_options = df["YEAR"].unique()
selected_year = st.select_slider("Select Decennial Census Year", options=year_options)
filtered_year_data = df[df["YEAR"] == selected_year]

# Remove/simplify large unneeded variables
counties = df.groupby("County", as_index=False).first()
del df
gc.collect()

# Change Level of Aggregation - State, SEA, and County
agg_options = ["State", "State Economic Area (Not Available for Boundaries)", "County"]
selected_agg_fake = st.selectbox("Select Level of Aggregation", options=agg_options)
if selected_agg_fake == agg_options[0]:
    selected_agg = "STATEICP"
elif selected_agg_fake == agg_options[1]:
    selected_agg_fake = "State Economic Area (SEA)"
    selected_agg = "SEA"
elif selected_agg_fake == agg_options[2]:
    selected_agg = "County"
selected_data = filtered_year_data.groupby(selected_agg)

# Change Demographic Variable
col_names = ["Age", "Sex", "Marital Status", "Race", "Hispanic" , "Birthplace"]
selected_var_fake = st.selectbox("Select Demographic Variable", options=col_names)
if selected_var_fake == col_names[0]:
    selected_var = "AGE"
elif selected_var_fake == col_names[1]:
    selected_var = "SEX"
elif selected_var_fake == col_names[2]:
    selected_var = "MARST"
elif selected_var_fake == col_names[3]:
    selected_var = "RACE"
elif selected_var_fake == col_names[4]:
    selected_var = "HISPAN"
elif selected_var_fake == col_names[5]:
    selected_var = "BPL"   
#summary_table_MAIN = selected_data[selected_var].value_counts()

# Change Visualization - Graduated Colors vs Dot Density
selected_vis = st.radio("Select Visualization Method: ",["Clickable Icons", "Boundaries Map", "Clickable Icons with Boundaries Map"])
st.write("")

# Create Map
m = folium.Map(location=[39, -96] , zoom_start=4) #starts in roughly center of U.S.

# Applys visualization based on "selected_vis" value
if selected_vis == "Clickable Icons":
    # Adds icon points for each geographic region - loops over each location in selected level of aggregation
    for geography in selected_data[selected_agg].unique():
        #geography = geography.astype(int)
        if selected_agg != "County":
            geography = geography[0].item() #converts to int
        else:
            geography = str(geography).strip("'[]'")
        
        # creates dataframe of obervations for the selected year and each location in state/SEA/county
        specific_geography = filtered_year_data[filtered_year_data[selected_agg] == geography]
        
        # gets total population for each location in state/SEA/county
        pop = specific_geography.shape[0] # num of rows
        
        # skips geography if population = 0
        if pop == 0:
            continue
            # if no population present, occasionally occurs at county level

        # creates summary table/basic statistics
        if selected_var != "AGE":
            summary_table = specific_geography[selected_var].value_counts()
        else:
            avg_age = specific_geography[selected_var].mean()
            avg_age = round(avg_age,2)
            mode_age = statistics.mode(specific_geography[selected_var])
    
        # redfines selected year
        year = specific_geography["YEAR"].unique()
            
        # gets info based on selected level of aggregation
        if selected_agg == "STATEICP":
            lat = specific_geography["state_latitude"].unique()
            lon = specific_geography["state_longitude"].unique()
            name = specific_geography["state_name"].unique()
        elif selected_agg == "SEA":
            lat = specific_geography["sea_lat"].unique()
            lon = specific_geography["sea_lon"].unique()
            s_name = specific_geography["state_name"].unique()
            sea = specific_geography["SEA"].unique()
            name = f"State:{s_name} <br> SEA:{sea}"
        elif selected_agg == "County":
            lat = counties[counties[selected_agg] == geography]["county_lat"].iloc[0]
            lon = counties[counties[selected_agg] == geography]["county_lon"].iloc[0]
            c_name = counties[counties[selected_agg] == geography]["county_name"].iloc[0]
            s_name = counties[counties[selected_agg] == geography]["state_name"].iloc[0]
            name = f"State:{s_name} <br> County:{c_name}"
    
        # displays info marker based on selected variable
        if selected_var == "SEX":
            if len(summary_table) == 1: # both sexes not present
                if summary_table[1]: #only males present
                    summary_table[2]=0
                elif summary_table[2]: #only females present
                    summary_table[1]=0   
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="orange"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br> Summary table of {selected_var_fake}: <br> Male - {summary_table[1]} <br> Female - {summary_table[2]}',
            ).add_to(m)
        elif selected_var == "AGE":
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="red"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Average Age: {avg_age} years <br><br>Most Common Age: {mode_age}',
            ).add_to(m)
        elif selected_var == "MARST":
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="green"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
            ).add_to(m)
        elif selected_var == "RACE":
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="lightblue"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
            ).add_to(m) 
        elif selected_var == "HISPAN":
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="darkblue"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
            ).add_to(m)
        elif selected_var == "BPL":
            if len(summary_table) == 1:
                if summary_table[0]: # only foreign births
                    summary_table[1]=0
                elif summary_table[1]: # no foreign births
                    summary_table[0]=0   
            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="purple"),
                popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: <br> Within U.S. - {summary_table[1]} <br> Outside U.S. - {summary_table[0]}',
            ).add_to(m)
elif selected_vis == "Boundaries Map":
    # read in and display json files
    if selected_agg == "STATEICP":
        with open(r"C:\Users\alexi\OneDrive\Documents\ASUGrad\2024 Fall\MFG598 Python\Final Project\Data\us-states.json","r") as file:
            geo_json = json.load(file)
        folium.GeoJson(geo_json,style_function=lambda feature: {
            "fillColor": "#514981 ",
            "color": "gray",
            "weight": 0.5}).add_to(m)
    elif selected_agg == "County":
        with open("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/us-counties.json","r") as file:
            geo_json = json.load(file)
        folium.GeoJson(geo_json,style_function=lambda feature: {
            "fillColor": "#514981 ",
            "color": "gray",
            "weight": 0.5}).add_to(m)
    elif selected_agg == "SEA":
        alert = """
        
        :blue-background[Warning: Please select State or County to display the boundaries map.]

        """
        st.markdown(alert)

elif selected_vis == "Clickable Icons with Boundaries Map":
    
    # Same as selected_vis == boundaries map
    if selected_agg == "STATEICP":
        with open(r"C:\Users\alexi\OneDrive\Documents\ASUGrad\2024 Fall\MFG598 Python\Final Project\Data\us-states.json","r") as file:
            geo_json = json.load(file)
        folium.GeoJson(geo_json,style_function=lambda feature: {
            "fillColor": "#514981 ",
            "color": "gray",
            "weight": 0.5}).add_to(m)
    elif selected_agg == "County":
        with open("C:/Users/alexi/OneDrive/Documents/ASUGrad/2024 Fall/MFG598 Python/Final Project/Data/us-counties.json","r") as file:
            geo_json = json.load(file)
        folium.GeoJson(geo_json,style_function=lambda feature: {
            "fillColor": "#514981 ",
            "color": "gray",
            "weight": 0.5}).add_to(m)
    elif selected_agg == "SEA":
        alert = """
        
        :blue-background[Warning: Please select State or County to display the boundaries map.]

        """
        st.markdown(alert)

    # Similar to as selected_vis == Clickable Icons
    # returns error previous if trying to apply to SEA level of aggregation        
    if selected_agg != "SEA":
        # Adds icon points for each geographic region - loops over each location in selected level of aggregation
        for geography in selected_data[selected_agg].unique():
            #geography = geography.astype(int)
            if selected_agg != "County":
                geography = geography[0].item() #converts to int
            else:
                geography = str(geography).strip("'[]'")
            
            # creates dataframe of obervations for the selected year and each location in state/SEA/county
            specific_geography = filtered_year_data[filtered_year_data[selected_agg] == geography]
            
            # gets total population for each location in state/SEA/county
            pop = specific_geography.shape[0] # num of rows
            
            # skips geography if population = 0
            if pop == 0:
                continue
                # if no population present, occasionally occurs at county level
        
            # creates summary table/basic statistics
            if selected_var != "AGE":
                summary_table = specific_geography[selected_var].value_counts()
            else:
                avg_age = specific_geography[selected_var].mean()
                avg_age = round(avg_age,2)
                mode_age = statistics.mode(specific_geography[selected_var])
        
            # redfines selected year
            year = specific_geography["YEAR"].unique()
                
            # gets info based on selected level of aggregation
            if selected_agg == "STATEICP":
                lat = specific_geography["state_latitude"].unique()
                lon = specific_geography["state_longitude"].unique()
                name = specific_geography["state_name"].unique()
            elif selected_agg == "SEA":
                lat = specific_geography["sea_lat"].unique()
                lon = specific_geography["sea_lon"].unique()
                s_name = specific_geography["state_name"].unique()
                sea = specific_geography["SEA"].unique()
                name = f"State:{s_name} <br> SEA:{sea}"
            elif selected_agg == "County":
                lat = counties[counties[selected_agg] == geography]["county_lat"].iloc[0]
                lon = counties[counties[selected_agg] == geography]["county_lon"].iloc[0]
                c_name = counties[counties[selected_agg] == geography]["county_name"].iloc[0]
                s_name = counties[counties[selected_agg] == geography]["state_name"].iloc[0]
                name = f"State:{s_name} <br> County:{c_name}"
        
            # displays info marker based on selected variable
            if selected_var == "SEX":
                if len(summary_table) == 1: # both sexes not present
                    if summary_table[1]: #only males present
                        summary_table[2]=0
                    elif summary_table[2]: #only females present
                        summary_table[1]=0   
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="orange"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br> Summary table of {selected_var_fake}: <br> Male - {summary_table[1]} <br> Female - {summary_table[2]}',
                ).add_to(m)
            elif selected_var == "AGE":
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="red"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Average Age: {avg_age} years <br><br>Most Common Age: {mode_age}',
                ).add_to(m)
            elif selected_var == "MARST":
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="green"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
                ).add_to(m)
            elif selected_var == "RACE":
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="lightblue"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
                ).add_to(m) 
            elif selected_var == "HISPAN":
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="darkblue"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: {summary_table}',
                ).add_to(m)
            elif selected_var == "BPL":
                if len(summary_table) == 1:
                    if summary_table[0]: # only foreign births
                        summary_table[1]=0
                    elif summary_table[1]: # no foreign births
                        summary_table[0]=0   
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.Icon(color="purple"),
                    popup=f'{name} ({year})<br><br>Total Population (1%): {pop}<br><br>Summary table of {selected_var_fake}: <br> Within U.S. - {summary_table[1]} <br> Outside U.S. - {summary_table[0]}',
                ).add_to(m)
                
     
# Display the map
st_folium(m, width=700, height=500, returned_objects=[])

# Write Current View
st.write(f"Displaying census data for the year {selected_year} for the variable {selected_var_fake}, aggregated to the {selected_agg_fake} level and displayed by {selected_vis}.")

