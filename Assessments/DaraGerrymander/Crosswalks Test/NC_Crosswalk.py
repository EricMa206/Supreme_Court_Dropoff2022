#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Libraries
import pandas as pd
import numpy as np
import geopandas


# In[2]:


ls


# In[3]:


# Load in shapefiles
precincts2016 = geopandas.read_file('SBE_PRECINCTS_20161004/PRECINCTS.shp')


# In[4]:


precincts2014 = geopandas.read_file('SBE_PRECINCTS_20141016/PRECINCTS.shp')


# In[5]:


# Create a unique id for each precinct in 2016 &2014
precincts2016['Prec_Uid'] = precincts2016['COUNTY_NAM'] + '|' + precincts2016['PREC_ID']
precincts2014['Prec_Uid'] = precincts2014['COUNTY_NAM'] + '|' + precincts2014['PREC_ID']


# In[6]:


precincts2016.info()


# In[7]:


# Preparing for matches for comparison
join2016 = precincts2016.astype({'geometry': str})
join2014 = precincts2014.astype({'geometry': str})


# In[8]:


fullmatch = join2016.merge(join2014, how='outer', on=['Prec_Uid', 'geometry'], suffixes=['16','14'])


# In[9]:


# Finding perfect matches (2609)
perfectmatch = fullmatch[['Prec_Uid', 'geometry', 'COUNTY_NAM16', 'COUNTY_NAM14']].dropna()
perfect = perfectmatch['Prec_Uid'].tolist()


# In[10]:


nonmatch16 = fullmatch[['Prec_Uid', 'geometry', 'ENR_DESC16']][fullmatch['COUNTY_NAM14'].isna()]
nonmatch14 = fullmatch[['Prec_Uid', 'geometry', 'ENR_DESC14']][fullmatch['COUNTY_NAM16'].isna()]


# In[11]:


# Finding perfect geometry matches (62)
geommatch = nonmatch16.merge(nonmatch14, 'inner', on='geometry', suffixes=['16','14'])
geom = geommatch['Prec_Uid16'].tolist()


# In[12]:


# Finded Precincts with the same id (4)
name = nonmatch16.merge(nonmatch14, 'inner', on='Prec_Uid', suffixes=['16','14'])['Prec_Uid'].tolist()


# In[13]:


# Geom does not match (2016:33, 2014:116)
mod16 = precincts2016[~precincts2016['Prec_Uid'].isin(perfect+geom)]
mod14 = precincts2014[~precincts2014['Prec_Uid'].isin(perfect+geom)]
mod16


# In[14]:


# Only checking against 2014 precincts that were not captured in Perfect or Geom matches
mod14_dict = mod14[['Prec_Uid', 'geometry']].to_dict('records')


# In[15]:


def check_merge(row):
    precincts = []
    for p in mod14_dict:
        if row['geometry'].contains(p['geometry']):
            precincts.append(p['Prec_Uid'])
    if len(precincts)>0:
        return precincts
    else:
        return np.nan


# In[16]:


def check_split(row):
    for p in mod14_dict:
        if row['geometry'].within(p['geometry']):
            return p['Prec_Uid']
    return np.nan


# In[17]:


mod16['Merge'] = mod16.apply(lambda i: check_merge(i), axis=1)
mod16['Split'] = mod16.apply(lambda i: check_split(i), axis=1)


# In[21]:


# Set index to make lookups easier
mod16.set_index('Prec_Uid',inplace=True)


# In[50]:


merged = mod16['Merge'][mod16['Merge'].notna()].to_dict()
split = mod16['Split'][mod16['Split'].notna()].to_dict()
merged


# In[30]:


# Load in returns
returns = pd.read_csv('NC_returns_3_16.csv')


# In[31]:


# Create a unique id for each precinct
returns['PrecReturns_id'] = returns['County'] + '|' + returns['Precinct']
returns


# In[32]:


# Create a crosswalk DataFrame named 'xwalk'.
# PrecReturns: Unique precinct id. To be merged on 'Prec_Uid'
# Match: 'PERFECT_MATCH', 'GEOM_MATCH', 'COUNTY_WIDE'
# Details: further details on each kind of match
xwalk = pd.DataFrame(returns['PrecReturns_id'].unique(), columns=['PrecReturns_id'])


# In[33]:


# Perfect matches
xwalk['Match'] = np.where(xwalk['PrecReturns_id'].isin(perfect), 'PERFECT_MATCH', 'UNKNOWN')
xwalk['Details'] = np.where(xwalk['PrecReturns_id'].isin(perfect), xwalk['PrecReturns_id'],'UNKNOWN')


# In[34]:


# Geometry perfectly matches
xwalk['Match'][(xwalk['Match']=='UNKNOWN') & (xwalk['PrecReturns_id'].isin(geom))] = 'GEOM_MATCH'
xwalk['Details'][xwalk['Match']=='GEOM_MATCH'] = xwalk['PrecReturns_id']


# In[64]:


xwalk['Match'][xwalk['PrecReturns_id'].isin(merged.keys())] = 'MERGED'
xwalk['Details'][xwalk['Match']=='MERGED'] = xwalk['PrecReturns_id'][xwalk['Match']=='MERGED'].apply(lambda i: merged[i])


# In[65]:


xwalk['Match'][xwalk['PrecReturns_id'].isin(split.keys())] = 'SPLIT'
xwalk['Details'][xwalk['Match']=='SPLIT'] = xwalk['PrecReturns_id'][xwalk['Match']=='SPLIT'].apply(lambda i: split[i])


# In[68]:


set([i.split('|')[1] for i in xwalk['PrecReturns_id'][xwalk['Match']=='UNKNOWN']])


# In[69]:


re_substr = '(\|ABS)|(\|CURB)|(\|ONE)|(\|OS)|(\|PROVI)|(\|TRANSFER)'


# In[70]:


# Labeling matches on county level unsorted ballots as 'County_Level'. Details: Precinct ID.
xwalk['Match'][xwalk['Match']=='UNKNOWN'] = np.where(xwalk['PrecReturns_id'][xwalk['Match']=='UNKNOWN'].str.contains(re_substr), 'COUNTY_LEVEL', 'UNKNOWN')


# In[113]:


xwalk['Details'][xwalk['Match']=='COUNTY_LEVEL'] = xwalk[xwalk['Match']=='COUNTY_LEVEL'].apply(lambda i: i['PrecReturns_id'].split('|')[1], axis=1)


# In[91]:


oldgeom = precincts2014['Prec_Uid'].tolist()
newgeom = precincts2016['Prec_Uid'].tolist()


# In[92]:


# Check if precinct id matches old 2014 id (10)
xwalk['Match'][(xwalk['Match']=='UNKNOWN') & (xwalk['PrecReturns_id'].isin(oldgeom))] = 'GEOM_OTHER'
xwalk['Details'][xwalk['Match']=='GEOM_OTHER'] = '2014 ' + xwalk['PrecReturns_id']


# In[97]:


# Unknown changes (5)
xwalk['Match'][(xwalk['Match']=='UNKNOWN') & (xwalk['PrecReturns_id'].isin(newgeom))] = 'GEOM_OTHER'


# In[99]:


# No matches found (3)
xwalk[(xwalk['Match']=='UNKNOWN')]


# In[115]:


xwalk.to_csv('NC_Crosswalk.csv')


# In[ ]:




