# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from __future__ import division
import pandas as pd
import numpy as np
from scipy import stats
import os
import dateutil
import csv
#-----matplotlib for charts
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as path
import seaborn as sns
#for popup
import tkinter as tk
from tkinter import ttk
import urllib
import json
from tkinter import messagebox
#for stratification------------------------------------
from sklearn.model_selection import train_test_split
#from sklearn import cross_validation, datasets
#import libraries
from datetime import datetime, timedelta,date
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.cluster import KMeans
# import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split
# import xgboost as xgb

#*****************************************
#               INPUT PARAMS
#*****************************************
import sys
import json
params = json.loads(sys.argv[1])
#print(params)
_chdir = params['workingDir']
_fileSource = params['fileSource']

#_filePath = params['uploadedFile'] if _fileSource == 'S3' else _filePath = 'check'
if _fileSource == 'S3': _filePath = '/path/to/S3/bucket'
else: _filePath = params['uploadedFile']
#*****************************************
print(_filePath)
os.chdir(_chdir) 
data = pd.read_csv(_filePath, encoding = "ISO-8859-1", engine='python')

data.head()
print(data.head(40))
data.info()
#create a macro variables
sample_size=0.1
var_list='Country,revenue_limit,freq_limit'

initial_data_size=data.shape[0]

print(sample_size)
print(var_list)
print(initial_data_size)

#table accruals without zero

#def quantile_func (var,value):
#    tab_non_zero=data[data[var]>0]
#    quantile_val=tab_non_zero[var].quantile([.25,.50,.75]).astype('float64')
#    #np.quantile(tab_non-zero[+var],value)
#    return quantile_val

customer_agg = data.groupby(['CustomerID','Country'],as_index=False).agg({'UnitPrice':'sum', 'InvoiceDate':'count'})
customer_agg = customer_agg.rename(columns={'InvoiceDate':'Frequency','UnitPrice':'Revenue'})

kmeans = KMeans(n_clusters=4)
kmeans.fit(customer_agg[['Frequency']])
customer_agg['FrequencyCluster'] = kmeans.predict(customer_agg[['Frequency']])

kmeans = KMeans(n_clusters=4)
kmeans.fit(customer_agg[['Revenue']])
customer_agg['RevenueCluster'] = kmeans.predict(customer_agg[['Revenue']])


def quantile_func (var,value):
    tab_non_zero=customer_agg[customer_agg[var]>0]
    quantile_val=tab_non_zero[var].quantile([value]).astype('float64')
    #np.quantile(tab_non-zero[+var],value)
    return quantile_val

Revenue_25=quantile_func(var='Revenue', value=.25)
Revenue_50=quantile_func(var='Revenue', value=.50)
Revenue_75=quantile_func(var='Revenue', value=.75)

print(Revenue_25[0.25])
print(Revenue_50[0.5])
print(Revenue_75[0.75])

Frequency_25=quantile_func(var='Frequency', value=.25)
Frequency_50=quantile_func(var='Frequency', value=.50)
Frequency_75=quantile_func(var='Frequency', value=.75)

print(Frequency_25)
print(Frequency_50)
print(Frequency_75)

# create ranges variables ---------------------
customer_agg.loc[(customer_agg['Revenue']>0) & (customer_agg['Revenue'] <= Revenue_50[0.5]) ,'revenue_limit']='[1-'+ str(Revenue_50[0.5])+']'
customer_agg.loc[(customer_agg['Revenue']>Revenue_50[0.5]) & (customer_agg['Revenue'] <= Revenue_75[0.75]) ,'revenue_limit']='['+ str(Revenue_50[0.5])+'-' + str(Revenue_75[0.75])+']'
customer_agg.loc[(customer_agg['Revenue']>Revenue_75[0.75])  ,'revenue_limit']='['+str(Revenue_75[0.75])+'+]'
customer_agg.loc[(customer_agg['Revenue']==0),'revenue_limit']="zero"

customer_agg.loc[(customer_agg['Frequency']>0) & (customer_agg['Frequency'] <= Frequency_50[0.5]) ,'freq_limit']='[1-'+ str(Frequency_50[0.5])+']'
customer_agg.loc[(customer_agg['Frequency']>Frequency_50[0.5]) & (customer_agg['Frequency'] <= Frequency_75[0.75]) ,'freq_limit']='['+ str(Frequency_50[0.5])+'-' + str(Frequency_75[0.75])+']'
customer_agg.loc[(customer_agg['Frequency']>Frequency_75[0.75])  ,'freq_limit']='['+str(Frequency_75[0.75])+'+]'
customer_agg.loc[(customer_agg['Frequency']==0),'freq_limit']="zero"

print(customer_agg.groupby('revenue_limit').agg([len]))
print(customer_agg.groupby('freq_limit').agg([len]))

customer_agg.revenue_limit.value_counts()
customer_agg.freq_limit.value_counts()

_=plt.hist(customer_agg['Frequency'],bins='auto',density=True,color='brown')

sns.distplot(customer_agg['Frequency'],
             hist=True,
             kde=False, #kde=False,
             bins=[0,1,2,3,4,5,7,8,9,24],
             color='blue',
             hist_kws={'edgecolor':'black'},
             kde_kws={'linewidth': 1}
             )
plt.title('Shobing Distribution')
plt.xlabel('# Of visits (l12M)')
plt.ylabel('# Of customers')           
plt.savefig('output/shopping distribution')
           
#stratification------------------------------------------------------------------
#var_list=['Activity','Card_Holder','Tier,revenue_limit','segment_limit','Gender','Family_Type','redemption_limit']
#zip(var_list)


#equivalent proc summary

def agg_var(var):
    return customer_agg.groupby(var).agg(number_of_members=pd.NamedAgg(column='CustomerID',aggfunc=len))
    
print(agg_var(var='Country'))
print(agg_var(var='revenue_limit'))
print(agg_var(var='freq_limit'))

#************* summarize the table data *********************************
#just count
#summery_data=data.groupby(['Family_Type','Tier','Gender','seg_limit','red_limit','revenue_limit'],as_index=False)['GRP_number'].count()


var_list.split(',')

#add averages of several variables and rename them
summary_data=customer_agg.groupby(var_list.split(','),as_index=False).agg({'CustomerID':'count',
        'Frequency':'mean',
        'Revenue':'mean'})

summary_data.rename(columns={'CustomerID':'customer_count'},inplace=True)
one_class_tab=pd.DataFrame(summary_data[summary_data['customer_count']==1])


one_class_tab=one_class_tab[var_list.split(',')+'customer_count'.split(',')]
size=one_class_tab.size
dim=one_class_tab.ndim

shape=one_class_tab.shape #get the number of lines of the table - number of members who are unique in their strata
shape[0]


if shape[0]>0:
    customer_agg=pd.merge(customer_agg,one_class_tab,on=var_list.split(','),how='left')
    one_class_tab_details=pd.DataFrame(customer_agg[customer_agg['customer_count']==1])
    customer_agg=pd.DataFrame(customer_agg[customer_agg['customer_count']!=1])
else:
    print('there is no class/strata with one members')
    

#get a separate data 
    

test=customer_agg.groupby(var_list.split(','),as_index=False).agg({'CustomerID':'count'})

#create 2 lists (control and target)
tab_train,tab_test= train_test_split(customer_agg, test_size=sample_size, stratify=customer_agg[var_list.split(',')])

customer_agg.shape

#tab_train,tab_test= train_test_split(data, test_size=sample_size, random_state=0, stratify=data[['Family_Type','Tier','Gender','seg_limit','red_limit','revenue_limit']]) #,'Card_Holder','Gender']])

df_tab_train=pd.DataFrame(tab_train)
df_tab_test=pd.DataFrame(tab_test)

print(len(df_tab_train.index))
print(len(df_tab_test.index))

df_tab_train['group']='target'
df_tab_test['group']='control'


if shape[0]>0:
    one_class_tab_details['group']='target'
    #one_class_tab_details.drop(['members_count'])
    frames=[df_tab_train,df_tab_test,one_class_tab_details]
else:
    frames=[df_tab_train,df_tab_test]
    
#append both table before runing the t-test    
final_tab=pd.concat(frames)
final_tab.shape[0]   


# #check records count
# if final_tab.shape[0]==initial_data_size:
#     print('The final table has a good count. Go ahead for the t-test')
#     messagebox.showinfo(title="Final Table Count Check",message="The final table has a good count. Go ahead for the t-test")
# else:
#     messagebox.showinfo(title="Final Table Count Check",message="there is an issue with the data, the count doesnt match")
#     print('there is an issue with the data, the count doesn\'t match')

def categorie_count(tab,var):
    cnt=tab.groupby([var])['CustomerID'].count().rename('count')
    #print('Table name is:' + tab)
    return print(cnt/len(tab.index))

 
#check stratification-----------------------------
print("train table:") 
categorie_count(tab=df_tab_train,var='Country')
print("test table:")
categorie_count(tab=df_tab_test,var='Country')
print('\n')
print("train table:")
categorie_count(tab=df_tab_train,var='revenue_limit')
print("test table:")
categorie_count(tab=df_tab_test,var='revenue_limit')
print('\n')
print("train table:")
categorie_count(tab=df_tab_train,var='freq_limit')
print("test table:")
categorie_count(tab=df_tab_test,var='freq_limit')
print('\n')
   
#-----------------------------------------------------------------------

final_tab.info() 
final_tab.groupby('group')['CustomerID'].count()
 
data.groupby('Country').agg(number_of_members=pd.NamedAgg(column='CustomerID',aggfunc=len))

# Equivalent proc summary: check averages by group
summary_tab=final_tab.groupby('group').agg({
        'CustomerID':'count',
        'Revenue':'mean',
        'Frequency':'mean'
                         })
summary_tab.columns=['customer_count','avg_segments','avg_revenue']
print('***** Below the average which we will run for the t-test*****\n')
print(summary_tab)


test=final_tab.groupby('group').agg({'Frequency':'mean'})
test.iloc[0,0]#control
test.iloc[1,0] # target

# t-test validation
def mean_test(var):
     print('***** The averages of are:\n')
     averages=final_tab.groupby('group').agg({var:'mean'})
     avegare_target=averages.iloc[1,0]
     aveage_control=averages.iloc[0,0]
     print(final_tab.groupby('group').agg({var:'mean'}))
     groups=pd.unique(final_tab.group.values)
     d_data = {grp:final_tab[var][final_tab.group == grp] for grp in groups}
     #is_normal=stats.norm.rvs(d_data['train'], d_data['test'])
     F, p = stats.f_oneway(d_data['target'], d_data['control'])
     #-----------------------
     print(p)
     print(F)
     print(var+'----------------------------')
     print("p-value for significance is: ", p)
     if p < 0.05:
         comment="reject null hypothesis"
         print(comment)
     else:
         comment="accept null hypothesis"
         print("accept null hypothesis")
     print('\n') 
     print(var+'- Test if distribution is not normal-----------')
     F2, p2 = stats.kruskal(d_data['target'], d_data['control'])
     print("p-value for significance is: ", p2)
     print('\n')
     sns.boxplot(x='group', y=var, data=final_tab, palette="Set1")
     with open('output/'+var+'_ttest_results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["variable", "average target","average control","p-value", "F","comment"])
        writer.writerow([var,avegare_target,aveage_control, p,F,comment])
     return p

        
mean_test(var='Revenue')
mean_test(var='Frequency')

 
#'Gender','Family_Type','Age_Group','Activity','Card_Holder','Tier','FFP_segment','Nationality','Country','Version','group'

groups_summary=final_tab.groupby(['Country','group'],as_index=False).agg({'CustomerID':'count',
                                                            'Revenue':'sum',
                                                            'Frequency':'sum'
                                                           
                                                            })


#todo
groups_summary.to_csv("output/demographics_groups.csv")

#### export  results -----------------------------------------
groups_selection_tab=final_tab[['CustomerID','group']]
groups_selection_tab.to_csv("output/selected_groups.csv")

#Charts to be in the dasboard

# rev_country = groups_summary.groupby("Country")["Revenue"].sum().sort_values()
# rev_country.plot(kind="barh", fontsize=4)

# plt.savefig('output/revenue_country')

# data.info()
# rev_date = data.groupby("InvoiceDate")["UnitPrice"].sum().sort_values()
# rev_date.plot(x ='InvoiceDate', y='UnitPrice', kind = 'line')
# plt.show()
# plt.savefig('output/trend')

# df = pd.DataFrame(groups_summary,columns=['Country','Revenue'])
# df.plot(x ='Country', y='Revenue', kind = 'bar')
# plt.show()


# df = groups_summary.groupby("group")["Revenue"].sum().sort_values()
# df.plot(x ='group', y='Revenue', kind = 'bar')
# plt.show()


