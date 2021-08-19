#!/usr/bin/env python
# coding: utf-8

# Requirement: Start looking at the compensation data set and start to figure out how to put the two data sources together.  
# Source: Compensation data, WRDS data.
# And I chose to use jupyter notebook.

# ## 1. Preparation
# Preparation work includes installing modules and importing libraries (i.e., numpy, pandas, datetime, wrds) that I tended to use during coding.

# ### 1.1 Install 'wrds' module

# In[1]:


pip install wrds


# ### 1.2 Import libraries

# In[2]:


import numpy as np
import pandas as pd
import datetime as dt
import wrds


# ### 1.3 Look at basic information about 'wrds'

# In[3]:


help(wrds)


# ### 1.4 Get connected with wrds using my wrds account

# In[4]:


conn=wrds.Connection()


# In[5]:


conn.list_libraries()


# ## 2. WRDS data
# 
# I thought it might be interesting to see association between financial data (e.g., net income, sales, etc.) and characteristics of CD&A section. Hence, I downloaded relevant data from 'Compustat Daily Updates - Fundamentals Annual'. 

# ### 2.1 Obtain wrds data using sql query
# Common criteria for Compustat Fundamentals Annual (`funda`):
#  - consol = "C" (fully consolidated)
#  - indfmt = "INDL" (industrial format)
#  - datafmt = "STD" (standard format)
#  - posrc = "D" (domestic; USA and Canada)
#  
#  Additionally, there is another way to obtain wrds data:  
#  
#  comp = conn.get_table(library = 'comp', 
#                    table ='funda', 
#                        columns=['cik', 'conm','fyear', 'ni','sale', 'at','lt'])
# But I felt that using sql was much more convenient.

# In[6]:


comp=conn.raw_sql("""
                  SELECT cik,conm,fyear,ni,sale,at,lt
                  FROM comp.funda
                  WHERE (fyear between '2006' and '2016')
                  AND indfmt='INDL' AND datafmt='STD' AND popsrc='D' AND consol='C'
                  """)
comp.head()               


# One problem of this step is that it always took too long to get the dataframe. I have tried to search for more efficient methods but failed.

# ### 2.2 Check basic infomation about the comp dataframe

# In[7]:


comp.info()


# ### 2.3 Transform type of 'fyear' 

# In[8]:


comp['fyear']=comp['fyear'].astype(int)
comp.info()


# ## 3. Import compensatin excel
# The compensation excel was provided by Professor Greg and was located in the predefined path and renamed as SEC.xlsx.

# ### 3.1 Read excel, transform digit of cik.

# In[9]:


sec=pd.read_excel('SEC.xlsx', index_col=False,converters={'CIK':'{:0>10}'.format})
sec.head()


# ### 3.2 Choose useful columns

# In[10]:


sec1=sec.iloc[:,[0,2,5,-8,-7,-6,-5,-4,-3,-2,-1]]
sec1.head()


# ### 3.3 Transform column names into lower case for the convenience when coding

# In[11]:


sec1.columns=map(str.lower,sec1.columns)
sec1.head()


# ### 3.4 Transform all the company names into upper case to make company names consistent with those in wrds data.

# In[12]:


sec1['company name']=sec1['company name'].str.upper()
sec1.head()


# ### 3.5 Look at information about compensation data

# In[13]:


sec1.info()


# ## 4. Merge WRDS data with Executive Compensation Data
# 
# ### 4.1 I used left join to merge wrds data with compensation data on cik and year.
# 

# In[14]:


merge=pd.merge(sec1,comp,how='left',left_on=['cik','year'],right_on=['cik','fyear'])
merge.head()


# ### 4.2 Make the dataframe more organized

# In[15]:


merge1=merge.sort_values(['cik','year'],ignore_index=True)
merge1.head()


# ### 4.3 Delete the 'fyear' column as it is the same as the 'year' column

# In[16]:


merge2=merge1.drop('fyear',axis=1)
merge2


# In[17]:


merge2.info()


# ### 4.4 Drop duplicates

# In[18]:


merge3=merge2.drop_duplicates(subset=['cik','company name','year'],keep='first')
merge3.info()


# In[ ]:




