#!/usr/bin/env python
# coding: utf-8

# In[1]:


## Code to apply current ECV color logic to all entries in JHU country/province data + US states
## Also assign same IDs as used in ECV World Map


# In[2]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import csv
import json
import requests
from datetime import datetime


# In[3]:


df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

# fill NaN with blank string to create new column combining country & province
df = df.fillna('')
df['country_province'] = df['Country/Region'] + df['Province/State']

focus = df.copy().drop(['Lat','Long','Province/State','Country/Region'], axis=1).set_index(['country_province']).reset_index()


# In[4]:


#do_not_include = ['Antigua and Barbuda', 'Angola', 'Benin', 'Botswana', 
#                  'Burundi', 'Cabo Verde', 'Chad', 'Comoros', 
#                  'Congo (Brazzaville)', 'Congo (Kinshasa)',"Cote d'Ivoire", 'Central African Republic',
#                  'Diamond Princess', 'Equatorial Guinea',
#                  'Eritrea', 'Eswatini',   'Gabon', 
#                  'Gambia', 'Ghana', 'Grenada', 'Guinea', 'Guinea-Bissau',
#                  'Guyana', 'Lesotho', 'Liberia', 'Libya', 'Madagascar',
#                  'Malawi', 'Maldives', 'Mauritania', 'Mozambique',
#                  'MS Zaandam', 'Namibia', 'Nicaragua', 'Papua New Guinea',
#                  'Rwanda',   'Saint Lucia', 
#                  'Saint Vincent and the Grenadines', 'Sao Tome and Principe',
#                  'Seychelles', 'Sierra Leone', 'South Sudan', 'Suriname', 'Syria', 
#                  'Tanzania',   'Togo', 'Uganda', 'West Bank and Gaza',
#                  'Western Sahara', 'Yemen', 'Zambia', 'Zimbabwe']


# In[5]:


focus


# In[6]:


# convert "pivoted" data to "long form"
data = pd.melt(focus, id_vars=['country_province'], var_name='date', value_name='cases')
#print(data)
# convert date column
data['date'] = pd.to_datetime(data['date'], format= '%m/%d/%y')


# In[7]:


data


# In[8]:


# pivot data with countries as columns
pivot_cases = pd.pivot_table(data, index = "date", columns = "country_province", values= "cases")

## drop countries listed above
#pivot_cases = pivot_cases.drop(columns=do_not_include)


# In[9]:


pivot_cases


# # Kosovo correction

# In[10]:


## Kosovo correction using European CDC data

# read in data
'''
eurocdc = pd.read_csv("https://opendata.ecdc.europa.eu/covid19/casedistribution/csv").dropna()
print(eurocdc)
# add date column from year, month & day columns
eurocdc['date'] = pd.to_datetime(eurocdc["dateRep"])
print(eurocdc['date'])
'''
# In[11]:


# filter for Kosovo
#kosovo = eurocdc[eurocdc['countriesAndTerritories'] == 'Kosovo']


# In[12]:


#kosovo


# In[13]:


# only include date & cases columns ('cases' indicates daily new cases)
#kosovo = kosovo[['date', 'cases']]

# sort by date and set date as index
#kosovo = kosovo.sort_values('date').set_index('date')

# create new column 'Kosovo' with cumulative cases for the purpose of updating Kosovo column in pivot_cases
#kosovo['Kosovo'] = kosovo['cases'].cumsum()

# only include 'Kosovo' column
#kosovo = kosovo[['Kosovo']]


# In[14]:


#kosovo


# In[15]:


# update JHU values for Kosovo with European CDC values
# https://stackoverflow.com/questions/24768657/replace-column-values-based-on-another-dataframe-python-pandas-better-way
#pivot_cases.update(kosovo)


# In[16]:


pivot_cases


# In[17]:


# check to see if cases were properly updated for each date
pivot_cases['Kosovo']


# # Add Canadian province Nunavut

# In[18]:


## Adding Canadian province Nunavut as a column

# read in separate Canada province data
canada = pd.read_csv('https://raw.githubusercontent.com/ishaberry/Covid19Canada/master/timeseries_prov/cases_timeseries_prov.csv')

# convert date column
canada['date'] = pd.to_datetime(canada['date_report'], format= '%d-%m-%Y')


# In[19]:


# filter for Nunavut
nunavut = canada[canada['province'] == 'Nunavut']

# only include date & cumulative_cases columns
nunavut = nunavut[['date', 'cumulative_cases']]

# sort by date and set date as index
nunavut = nunavut.sort_values('date').set_index('date')

# rename cumulative_cases for the purpose of merging to JHU 'country_province'
nunavut = nunavut.rename(columns = {'cumulative_cases':'CanadaNunavut'})
print(nunavut)
# only include 'CanadaNunavut' column
nunavut = nunavut[['CanadaNunavut']]


# In[20]:


#nunavut


# In[21]:


# add Nunavut cases onto pivot_cases data frame
#pivot_cases = pivot_cases.join(nunavut)

#pivot_cases_test['CanadaNunavut'] = nunavut['CanadaNunavut']


# In[22]:


pivot_cases


# # Add US State data

# In[23]:


## Adding US states

us_states = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
#date,state,fips,cases,deaths
us_states['date'] = pd.to_datetime(us_states['date'], format= '%Y-%m-%d')
us_states['state']="US"+us_states['state']

# In[24]:


us_states


# In[25]:


# read in list of 2-letter state codes with state names
state_list = pd.read_csv('us_state_list.csv')

# add 'county_province' column for purpose of merging with map IDs later
state_list['country_province'] = "US" + state_list['state_name']


# In[26]:


state_list


# In[27]:


# merging full state names onto COVID Tracking Project data
#us_states = us_states.merge(state_list, on='state', how='left')


# In[28]:


print(us_states)


# In[29]:


# pivot data with "country_province" as columns and "positive" (total cases) as values
us_state_cases = pd.pivot_table(us_states, index = "date", columns = "state", values= "cases")
print(us_state_cases["USKansas"])
print(us_state_cases["USConnecticut"])

# In[30]:


us_state_cases


# In[31]:


# add US state cases onto pivot_cases data frame
pivot_cases = pivot_cases.join(us_state_cases)


# In[32]:


pivot_cases


# # End of US state addition

# In[33]:


# replace null values in pivot_cases with 0
pivot_cases.replace(np.nan, 0, inplace=True)


# In[34]:


pivot_cases


# In[35]:


# new dataframe to store "daily new cases"
pivot_newcases = pivot_cases.copy()

# calculate "daily new cases"
for column in pivot_newcases.columns[0:]:
    DailyNewCases = column
    pivot_newcases[DailyNewCases] = pivot_newcases[column].diff()


# In[36]:


# fill NaN in pivot_newcases (first row) with values from pivot_cases
pivot_newcases.fillna(pivot_cases, inplace=True)


# In[37]:


pivot_newcases


# In[38]:


# replace negative daily values by setting 0 as the lowest value
pivot_newcases = pivot_newcases.clip(lower=0)


# In[39]:


# new dataframe to store "avg new cases"
pivot_avgnewcases = pivot_newcases.copy()

# calculate 7-day averages of new cases
for column in pivot_avgnewcases.columns[0:]:
    DaySeven = column
    pivot_avgnewcases[DaySeven] = pivot_avgnewcases[column].rolling(window=7, center=False).mean()


# In[40]:


# fill NaN in pivot_avgnewcases (first 6 rows) with values from pivot_newcases
pivot_recentnew = pivot_avgnewcases.fillna(pivot_newcases)


# In[41]:


pivot_recentnew


# In[42]:


# new dataframe to store "avg new cases" with centered average
pivot_avgnewcases_center = pivot_newcases.copy()

# calculate 7-day averages of new cases with centered average
for column in pivot_avgnewcases_center.columns[0:]:
    DaySeven = column
    pivot_avgnewcases_center[DaySeven] = pivot_avgnewcases_center[column].rolling(window=7, min_periods=4, center=True).mean()


# In[43]:


pivot_avgnewcases_center


# In[44]:


## new dataframe to store "avg new cases" with centered average
#pivot_recentnew_peaktodate = pivot_recentnew.copy()

## calculate 7-day averages of new cases with centered average
#for column in pivot_recentnew_peaktodate.columns[0:]:
#    DaySeven = column
#    pivot_recentnew_peaktodate[DaySeven] = pivot_recentnew_peaktodate[column].cummax()


# In[45]:


#pivot_recentnew_peaktodate


# In[46]:


# new dataframe to store peak 7-day average to date 
pivot_recentnew_peaktodate = pivot_recentnew.cummax()


# In[47]:


pivot_recentnew_peaktodate


# In[48]:


# reset indexes of "pivoted" data
pivot_cases = pivot_cases.reset_index()
pivot_newcases = pivot_newcases.reset_index()
pivot_recentnew = pivot_recentnew.reset_index()
pivot_avgnewcases_center = pivot_avgnewcases_center.reset_index()
pivot_recentnew_peaktodate = pivot_recentnew_peaktodate.reset_index()


# In[49]:


# convert "pivot" of total cases to "long form"
country_cases = pd.melt(pivot_cases, id_vars=['date'], var_name='country', value_name='cases')


# In[50]:


country_cases


# In[51]:


# convert "pivot" of daily new cases to "long form"
country_newcases = pd.melt(pivot_newcases, id_vars=['date'], var_name='country', value_name='new_cases')


# In[52]:


country_newcases


# In[53]:


# convert "pivot" of recent new cases to "long form" (7-day avg w first 6 days from "new cases")
country_recentnew = pd.melt(pivot_recentnew, id_vars=['date'], var_name='country', value_name='recent_new')


# In[54]:


country_recentnew


# In[55]:


# convert "pivot" of centered average new cases to "long form"
country_avgnewcases_center = pd.melt(pivot_avgnewcases_center, id_vars=['date'], var_name='country', value_name='avg_cases')


# In[56]:


country_avgnewcases_center


# In[57]:


# convert "pivot" of centered average new cases to "long form"
country_recentnew_peaktodate = pd.melt(pivot_recentnew_peaktodate, id_vars=['date'], var_name='country', value_name='peak_recent_new')


# In[58]:


country_recentnew_peaktodate


# In[59]:


# merge the 5 "long form" dataframes based on index
country_merge = pd.concat([country_cases, country_newcases, country_avgnewcases_center, country_recentnew, country_recentnew_peaktodate], axis=1)


# In[60]:


# NOTE:
# original code uses integer from latest 7-day average in country color logic

# take integer from "recent_new"
country_merge['recent_new_int'] = country_merge['recent_new'].astype(int)


# In[61]:


# remove duplicate columns
country_merge = country_merge.loc[:,~country_merge.columns.duplicated()]


# In[62]:


country_merge


# In[63]:


## UPDATE 9/25/20 - modified green logic due to quirk caused by original logic on countries page
## original logic caused Uruguay with avg ~16 cases to appear red because 16 > 50% of its low peak of 24

## Orignial green logic:
## if state_color_test['recent_new_int'] <= n_0*f_0 or state_color_test['recent_new_int'] <= n_0 and state_color_test['recent_new_int'] <= f_0*state_color_test['peak_recent_new']:

#choosing colors
n_0 = 20
f_0 = 0.5
f_1 = 0.2

# https://stackoverflow.com/questions/49586471/add-new-column-to-python-pandas-dataframe-based-on-multiple-conditions/49586787
def conditions(country_merge):
    if country_merge['recent_new_int'] <= n_0:
        return 'green'
    elif country_merge['recent_new_int'] <= 1.5*n_0 and country_merge['recent_new_int'] <= f_0*country_merge['peak_recent_new'] or country_merge['recent_new_int'] <= country_merge['peak_recent_new']*f_1:
        return 'yellow'
    else:
        return 'red'

country_merge['color_historical'] = country_merge.apply(conditions, axis=1)


# In[64]:


country_merge


# In[65]:


# dataframe with only the most recent date for each country
# https://stackoverflow.com/questions/23767883/pandas-create-new-dataframe-choosing-max-value-from-multiple-observations
country_latest = country_merge.loc[country_merge.groupby('country').date.idxmax().values]


# In[66]:


country_latest


# In[67]:


# dataframe with just country, total cases, and color
country_total_color = country_latest[['country','cases','color_historical']]

# rename cases to total_cases and color_historical to color for the purpose of merging
country_total_color = country_total_color.rename(columns = {'cases':'total_cases', 'color_historical':'color'})


# In[68]:


print(country_total_color)


# # Merge latest JHU country/province colors with ECV world map id

# In[69]:


# read in csv of countries & provinces with id for ECV world map
worldmap = pd.read_csv('../classification_ids2_jhu.csv')

# fill NaN with blank string to create new column combining country & province
worldmap = worldmap.fillna('')
worldmap['country_province'] = worldmap['jhu_country'] + worldmap['jhu_province']


# In[70]:


worldmap


# In[71]:


# dropping unneccesary columns
worldmap_id = worldmap.drop(['jhu_province','jhu_country','Change'], axis=1)


# In[72]:


# create dataframe of latest color with id (to match Olga's country/province id for ECV world map)
latest_with_id = country_total_color.copy()
latest_with_id = latest_with_id.rename(columns = {'country':'country_province', 'color':'Change'})
#latest_with_id['country_province'] = latest_with_id['country_province'].replace({'Cabo Verde' : 'Cape Verde'})

# join latest color onto ECV world map data
latest_with_id = worldmap_id.merge(latest_with_id, on='country_province', how='left')

# change column order to match with original "classification_ids2" 
latest_with_id = latest_with_id[['province', 'country', 'id', 'value', 'color', 'Change', 'value_old', 'color_old']]


# In[73]:


latest_with_id


# In[74]:
print(latest_with_id)

latest_with_id.to_csv('classification_ids2.csv', index = False)

