#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Libraries
import pandas as pd


# In[2]:


ls


# In[3]:


# Load in returns from 2014
returns = pd.read_csv('results_sort_20141104.txt', sep='\t')


# In[4]:


returns


# In[5]:


# Filter out any columns that don't need to be aggregated. 
# Included only US Senate and statewide court elections
filt_col = ['County', 'Contest Name', 'Choice', 'Choice Party', 'Total Votes']


# In[6]:


filt_contest = '(US SENATE)|(NC SUPREME COURT)|(NC COURT OF APPEALS)'


# In[7]:


returns_filt = returns[filt_col][returns['Contest Name'].str.contains(filt_contest)]


# In[22]:


returns_filt.info()


# In[21]:


# Create a unique id for each candidate using their contest, name and party. These will become column headings
# Not filling empty Party names will produce errors
returns_filt['Choice Party'].fillna('', inplace=True)


# In[23]:


returns_filt['cand_id'] = returns_filt['Contest Name'] + '_' + returns_filt['Choice'] + '_' + returns_filt['Choice Party']


# In[24]:


# Drop elements in id
returns_filt.drop(['Contest Name', 'Choice', 'Choice Party'], axis=1, inplace=True)


# In[25]:


returns_filt


# In[32]:


# Sum the total votes, grouped by County and Candidate
# Unstack reshapes the table long to wide with Candidates for each column
agg2014 = returns_filt.groupby(by=['County','cand_id']).sum().unstack()


# In[33]:


agg2014


# In[34]:


agg2014.to_csv('Aggregate_Results_2014.csv')


# In[ ]:




