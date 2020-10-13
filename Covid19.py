#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import numpy as np


# In[2]:


df = pd.read_csv('covid_19_data.csv', index_col = ['SNo'])
print(df.head())


# In[3]:


# Check data types of each columns
df.dtypes
# Convert values of Observation Date & Last Update Date columns to DateTime value
df['ObservationDate'] = pd.to_datetime(df['ObservationDate'])
df['Last Update'] = pd.to_datetime(df['Last Update']).dt.date
df['Last Update'] = pd.to_datetime(df['Last Update'])
# check data types of these columns again
df.dtypes


# In[4]:


# Strip leading & trailing white space in 'Country/Region' and 'Province/State' columns
df['Country/Region'] = df['Country/Region'].str.strip()
df['Province/State'] = df['Province/State'].str.strip()


# Fixing some typo country names
df['Country/Region'] = df['Country/Region'].replace("('St. Martin',)", 'St. Martin')
df['Country/Region'] = df['Country/Region'].replace("Gambia, The", 'St. Martin')
df['Country/Region'] = df['Country/Region'].replace("Bahamas, The", 'The Bahamas')
df['Country/Region'] = df['Country/Region'].replace("occupied Palestinian territory", 'Palestine')
df['Country/Region'] = df['Country/Region'].replace("East Timor", 'Timor-Leste')
df['Country/Region'] = df['Country/Region'].replace("North Ireland", 'Ireland')


# Check # of countries in the dataset
countries = df['Country/Region'].unique()
print(len(countries))


# Omit records of countries that have less than 15 records as it is not sufficient for analytics
omitCountries = []
for country in countries:
    newCountry = df[df['Country/Region'] == country]
    totalRows = len(newCountry.index)
    if totalRows < 20:
        omitCountries.append(country)
print('Countries to be omitted:', omitCountries)

df = df.set_index('Country/Region') # Temporarily set Country/Region column as index
for country in omitCountries:
    df = df.drop(country, axis = 0)
df = df.reset_index() # Reset index

# Check # of countries again after fixing names
countries = df['Country/Region'].unique()
print(len(countries))


# In[5]:


# Find out the last date of the dataset
maxDate = df['ObservationDate'].max().strftime('%d/%m/%Y')

# Check to which country has 0 death as of the maxDate
countriesWithNoDeath = []
for country in countries:
    newDf = df[df['Country/Region'] == country]
    if (newDf[newDf['ObservationDate'] == maxDate]['Deaths'] == 0).all():
        countriesWithNoDeath.append(country)
print('There are ', len(countriesWithNoDeath), ' countries that have 0 death. They are', countriesWithNoDeath)


# In[6]:


# Split Dataset into noDeathCountries & CountriesHaveDeaths

# Create dataframe for noDeathCountries
noDeathCountries = pd.DataFrame()
for country in countriesWithNoDeath:
    newDf = df[df['Country/Region'] == country]
    noDeathCountries = noDeathCountries.append(newDf)

# Check to see if the new dataframe has the correct countries
print('There are ', len(noDeathCountries['Country/Region'].unique()), ' countries that have 0 deaths')

# Create dataframe for CountriesWithDeaths
CountriesWithDeaths = list(set(countries) ^ set(countriesWithNoDeath))
CountriesHaveDeaths = pd.DataFrame()
for country in CountriesWithDeaths:
    newDf = df[df['Country/Region'] == country]
    CountriesHaveDeaths = CountriesHaveDeaths.append(newDf)

# Check to see if the new dataframe has the correct countries
print('There are ', len(CountriesHaveDeaths['Country/Region'].unique()), ' countries that have deaths') # The result should be 213 - 37 = 176


# In[7]:


# Identify CountriesHaveDeaths with one or more unique Provinces 
countriesWithProvince = CountriesHaveDeaths[(CountriesHaveDeaths['Province/State'].notnull() == True)]['Country/Region'].unique()

# Identify CountriesHaveDeaths with more than one unique Province 
countriesWithMultipleProvinces = []
for country in countriesWithProvince:
    newDf = CountriesHaveDeaths[CountriesHaveDeaths['Country/Region'] == country]
    if len(newDf['Province/State'].unique()) > 1:
        countriesWithMultipleProvinces.append(country)
print("There are ", len(countriesWithMultipleProvinces), " countries that have multiple provinces.")
print("They are ", countriesWithMultipleProvinces)

# Get list of countries with one or no province
countriesWithOneOrNoProvince = list(set(CountriesHaveDeaths['Country/Region'].unique()) ^ set(countriesWithMultipleProvinces))
print("There are ", len(countriesWithOneOrNoProvince), " countries that have one or no province.")  # The result should be 176 - 27 = 149
print("They are ", countriesWithOneOrNoProvince)


# In[8]:


# Creating line chart of death trend for countries 
for country in countries:
    newCountry1 = df[df['Country/Region'] == country]
    newCountry2 = newCountry1.groupby(['ObservationDate']).sum().reset_index()
    fig, ax = plt.subplots(figsize = (20,10))
    plot1, = ax.plot(newCountry2['ObservationDate'], newCountry2['Deaths'], color = 'red', label='Deaths')
    ax.set_xlabel('Date')
    ax.set_ylabel('Deaths')
    ax2 = ax.twinx()
    plot2, = ax2.plot(newCountry2['ObservationDate'], newCountry2['Recovered'], color = 'blue',label='Recovered')
    ax2.set_ylabel('Recovered')
    ax2.legend(handles = [plot1, plot2], loc = 'upper left')
    ax.set_title('Line Chart Showing Death Trend in ' + str(country))
    plt.show()


# In[9]:


# Create a dataframe in which each country only has one record on the lastest updated date
df1 = df.groupby(['Country/Region','ObservationDate']).sum().reset_index()
df4 = pd.DataFrame(columns = ['Country/Region', 'ObservationDate', 'Confirmed','Deaths','Recovered'])
for country in countries:
    df2 = df1[df1['Country/Region'] == country]
    df3 = df2[df2['ObservationDate'] == df2['ObservationDate'].max()].reset_index(drop=True)
    df4 = df4.append(df3, ignore_index = True)
    df4 = df4.sort_values('Country/Region')
print(df4)


# In[10]:


fig = go.Figure(data=go.Choropleth(
    locations=df4['Country/Region'], # Spatial coordinates
    z = df4['Deaths'], # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "# of deaths",
))

fig.update_layout(
    title_text = "World's Death Statistics Due to Coronavirus",
    geo_scope='world', # limite map scope to USA
)

fig.show()
#Note that not all countries have the same latest updated date


# In[11]:


fig = go.Figure(data=go.Choropleth(
    locations=df4['Country/Region'], # Spatial coordinates
    z = df4['Recovered'], # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Blues',
    colorbar_title = "# of recoveries",
))

fig.update_layout(
    title_text = "World's Recovered Statistics Due to Coronavirus",
    geo_scope='world', # limite map scope to USA
)

fig.show()

#Recovered Data of US is not accurate


# In[12]:


fig = go.Figure(data=go.Choropleth(
    locations=df4['Country/Region'], # Spatial coordinates
    z = df4['Confirmed'], # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Greens',
    colorbar_title = "# of Confirmed Cases",
))

fig.update_layout(
    title_text = "World's Infected Cases Due to Coronavirus",
    geo_scope='world', # limite map scope to USA
)

fig.show()


# In[13]:


# Add 3 more columns to the df4 dataframe 
df4['activeCases'] = df4['Confirmed'] - df4['Deaths'] - df4['Recovered']
df4['deathRate'] = (df4['Deaths']/df4['Confirmed']) * 100
df4['recoveryRate'] = (df4['Recovered']/df4['Confirmed']) * 100
df4['activeCasesRate'] = (df4['activeCases']/df4['Confirmed']) * 100
df4


# In[27]:


fig = go.Figure()
fig.add_trace(go.Bar(
    y=df4['deathRate'],
    x=df4['Country/Region'],
    name="Death %",
    marker=dict(
        color='rgba(0,128,0, 0.6)',
        line=dict(color='rgba(0,128,0, 0.5)', width=0.05)
    )
))
fig.add_trace(go.Bar(
    y=df4['recoveryRate'],
    x=df4['Country/Region'],
    name="Recovery %",
    marker=dict(
        color='rgba(0,0,255, 0.6)',
        line=dict(color='rgba(0,0,255, 0.5)', width=0.05)
    )
))
fig.add_trace(go.Bar(
    y=df4['activeCasesRate'],
    x=df4['Country/Region'],
    name="Active %",
    marker=dict(
        color='rgba(128,0,0, 0.5)',
        line=dict(color='rgba(128,0,0, 0.5)', width=0.05)
    )
))
fig.update_layout(
        yaxis=dict(
        title_text="Marks %",
        ticktext=["0%", "20%", "40%", "60%","80%","100%"],
        tickvals=[0, 20, 40, 60, 80, 100],
        tickmode="array",
        titlefont=dict(size=15),
    ),
    autosize=False,
    width=1500,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    title={
        'text': "Coronavirus's Active, Death & Recovery Rate of All Countries",
        'y':0.96,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    barmode='stack')
fig.show()


# In[26]:


# Calculate the overall death rate and recovery rate of all countries
worldDeathRate = round(((df4['Deaths'].sum()/df4['Confirmed'].sum()) * 100),2)
worldRecoveryRate = round(((df4['Recovered'].sum()/df4['Confirmed'].sum()) * 100),2)
print("The Coronavirus's world death rate is {}%".format(worldDeathRate))
print("The Coronavirus's world recovery rate is {}%".format(worldRecoveryRate))


# In[ ]:




