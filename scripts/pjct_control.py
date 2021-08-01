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
import boto3
import io 
from pandas_profiling import ProfileReport
import statsmodels.api as sm
from statsmodels.formula.api import ols


#*****************************************
#               INPUT PARAMS
#*****************************************
import sys
import json
params = json.loads(sys.argv[1])

nb_groups = params['nb_groups']
group1_pct = params['group1_pct']
group2_pct = params['group2_pct']
group3_pct = params['group3_pct']
stratification_var0 = params['st_var0']
stratification_var1 = params['st_var1']
stratification_var2 = params['st_var2']
stratification_var3 = params['st_var3']
stratification_var4 = params['st_var4']
stratification_var5 = params['st_var5']
id_variable = params['id_variable']
#*****************************************


#-----------------Paremeters---------------
ftp=1
"""
nb_groups=3
group1_pct=0.4
group2_pct=0.4
group3_pct=0.2

stratification_var0='StockCode'
stratification_var1='Description'
stratification_var2='Country'
stratification_var3='Quantity'
stratification_var4='UnitPrice'
stratification_var5=''

id_variable='CustomerID'
"""

initial_selected_var_list=stratification_var0+','+stratification_var1+','+stratification_var2+','+stratification_var3+','+stratification_var4+','+stratification_var5

cat_limit=10

#---------------
# get your credentials from environment variables
aws_id = 'AKIA5IM6XOLZZJTX5VPN'
aws_secret = 'aRuopnL+fQWlKMFfmA58d8PVEFLqMBQQkgycxy1k'
s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
bucket= 'application-aws-version'
file_path = "control_group_selection/customer_tab3.csv"
obj = s3.get_object(Bucket= bucket, Key= file_path)
body = obj['Body']
csv_content = body.read().decode('utf-8').splitlines()#"ISO-8859-1 utf-8
csv_data = csv.DictReader(csv_content)
json_data = []
for csv_row in csv_data:
    json_data.append(csv_row)
jsonString = json.dumps(json_data)
print(jsonString)
data = pd.read_json(jsonString)
data.head()

#--------------------------


# os.chdir("C:/Users/AHAB2/Documents/Ahmad documents/perso/dependants docs/project/control_group")


data.info()
data.describe()
type(data)
var_types=data.dtypes


if any(data[id_variable].duplicated())==True:
    print('The table has duplicates')
    data=data.drop_duplicates(id_variable)
    
initial_data_size=data.shape[0]

def quantile_func (var,value):
    tab_non_zero=data[data[var]>0]
    quantile_val=tab_non_zero[var].quantile([value]).astype('float64')
    return quantile_val


#------------- output list for the user ---------------------
cat_var_list=""
counter=0
for col in range(0,data.shape[1]):    
        counter=counter+1
        if counter==1:
            cat_var_list=cat_var_list+data.columns[col]
            print(cat_var_list)
        else:
            cat_var_list = cat_var_list + ',' + data.columns[col]

cat_var_list.split(',')
var_table=pd.DataFrame(cat_var_list.split(','),columns=["var_list"])
json_cat_var=var_table.to_json(orient="split")
jsonBuffer = io.StringIO()
json_cat_var=var_table.to_json(jsonBuffer)
session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
s3 = session.resource('s3')
s3.Object(bucket, 'control_group_selection/user_form_paramaters/cat_var_list.json').put(Body= jsonBuffer.getvalue())
data.info()    

len(cat_var_list.split(','))
data.columns[1]

data.info()
final_strata_vars=""
select_numeric_vars=""
counter=0
for i in range(0,len(initial_selected_var_list.split(','))-1):
    print(i)
    if (initial_selected_var_list.split(','))[i]!="":
        try:
            if ((data[(initial_selected_var_list.split(','))[i]].str.isalpha()*1).sum())>0:
                cat_list=data[(initial_selected_var_list.split(','))[i]].value_counts()
                counter=+counter
                if cat_list.shape[0]>cat_limit:
                    agg_cat=data.groupby((initial_selected_var_list.split(','))[i],as_index=False).agg({id_variable:'count'})
                    agg_cat=agg_cat.sort_values(id_variable,ascending=False)
                    top_agg_cat=(agg_cat.head(cat_limit))[[(initial_selected_var_list.split(','))[i]]]
                    data=pd.merge(data,top_agg_cat,on=(initial_selected_var_list.split(','))[i],how='left',indicator=True)
                    data.loc[data._merge=="left_only",(initial_selected_var_list.split(','))[i]+'_grouped']='other'
                    data.loc[data._merge=="both",(initial_selected_var_list.split(','))[i]+'_grouped']=data[(initial_selected_var_list.split(','))[i]]
                    if counter==1:
                        final_strata_vars=final_strata_vars+(initial_selected_var_list.split(','))[i]+'_grouped'
                    else:
                        final_strata_vars = final_strata_vars + ',' + (initial_selected_var_list.split(','))[i]+'_grouped'
                    del data['_merge']
                else:
                    if counter==1:
                        final_strata_vars=final_strata_vars+(initial_selected_var_list.split(','))[i]
                    else:
                        final_strata_vars = final_strata_vars + ',' + (initial_selected_var_list.split(','))[i]
            else:
                quant_25=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.25)
                quant_50=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.50)
                quant_75=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.75)
                data.loc[(data[(initial_selected_var_list.split(','))[i]]>0) & (data[(initial_selected_var_list.split(','))[i]] <= quant_50[0.5]) ,(initial_selected_var_list.split(','))[i]+'_limit']='[1-'+ str(quant_50[0.5])+']'
                data.loc[(data[(initial_selected_var_list.split(','))[i]]>quant_50[0.5]) & (data[(initial_selected_var_list.split(','))[i]] <= quant_75[0.75]) ,(initial_selected_var_list.split(','))[i]+'_limit']='['+ str(quant_50[0.5])+'-' + str(quant_75[0.75])+']'
                data.loc[(data[(initial_selected_var_list.split(','))[i]]>quant_75[0.75])  ,(initial_selected_var_list.split(','))[i]+'_limit']='['+str(quant_75[0.75])+'+]'
                data.loc[(data[(initial_selected_var_list.split(','))[i]]==0),(initial_selected_var_list.split(','))[i]+'_limit']="zero"
                if counter==1:
                    final_strata_vars=final_strata_vars+(initial_selected_var_list.split(','))[i]+'_limit'
                    select_numeric_vars=select_numeric_vars+(initial_selected_var_list.split(','))[i]
                else:
                    final_strata_vars = final_strata_vars + ',' + (initial_selected_var_list.split(','))[i]+'_limit'
                    select_numeric_vars=select_numeric_vars + ',' + (initial_selected_var_list.split(','))[i]
        except Exception: #in case an issue in the isalpha() then we consider that the variable is numeric and we proceed for the below.
            quant_25=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.25)
            quant_50=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.50)
            quant_75=quantile_func(var=(initial_selected_var_list.split(','))[i], value=.75)
            data.loc[(data[(initial_selected_var_list.split(','))[i]]>0) & (data[(initial_selected_var_list.split(','))[i]] <= quant_50[0.5]) ,(initial_selected_var_list.split(','))[i]+'_limit']='[1-'+ str(quant_50[0.5])+']'
            data.loc[(data[(initial_selected_var_list.split(','))[i]]>quant_50[0.5]) & (data[(initial_selected_var_list.split(','))[i]] <= quant_75[0.75]) ,(initial_selected_var_list.split(','))[i]+'_limit']='['+ str(quant_50[0.5])+'-' + str(quant_75[0.75])+']'
            data.loc[(data[(initial_selected_var_list.split(','))[i]]>quant_75[0.75])  ,(initial_selected_var_list.split(','))[i]+'_limit']='['+str(quant_75[0.75])+'+]'
            data.loc[(data[(initial_selected_var_list.split(','))[i]]==0),(initial_selected_var_list.split(','))[i]+'_limit']="zero"
            if counter==1:
                    final_strata_vars=final_strata_vars+(initial_selected_var_list.split(','))[i]+'_limit'
                    select_numeric_vars=select_numeric_vars+(initial_selected_var_list.split(','))[i]
            else:
                final_strata_vars = final_strata_vars + ',' + (initial_selected_var_list.split(','))[i]+'_limit'
                select_numeric_vars=select_numeric_vars + ',' + (initial_selected_var_list.split(','))[i]


from matplotlib.backends.backend_agg import FigureCanvasAgg
for i in range(0,len(select_numeric_vars.split(','))):
    if (select_numeric_vars.split(','))[i]!="":
        
        print("********************************************")
        print((select_numeric_vars.split(','))[i])
        print(i)
        print("********************************************")
        sns.distplot(data[(select_numeric_vars.split(','))[i]],
                     hist=True,
                     kde=False, #kde=False,
                     bins=[0,1,2,3,4,5,6,7,8,9,10,11,15,16,17,18,19,20], #7,8,9,24
                     color='blue',
                     hist_kws={'edgecolor':'black'},
                     kde_kws={'linewidth': 1}
                     )
        plt.title((select_numeric_vars.split(','))[i])
        plt.xlabel((select_numeric_vars.split(','))[i])
        plt.ylabel('# Of customers')   
        plt.savefig('output/'+(select_numeric_vars.split(','))[i])
        plt.show()



#--------------------export tables for the output dashboard-------------------------------------

for i in range(0,len(final_strata_vars.split(','))):
    if (final_strata_vars.split(','))[i]!="": 
        stat_tab=data.drop_duplicates(subset=[(final_strata_vars.split(','))[i],id_variable])
        stat_tab=pd.DataFrame(stat_tab[(final_strata_vars.split(','))[i]].value_counts().reset_index())
        stat_tab.rename(columns={(final_strata_vars.split(','))[i]:'nb_members'},inplace=True)
        stat_tab.rename(columns={'index':(final_strata_vars.split(','))[i]},inplace=True)
        jsonBuffer = io.StringIO()
        session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
        s3 = session.resource('s3')
        stat_tab.to_json(jsonBuffer, orient='values');
        s3.Object(bucket, 'control_group_selection/results/dashboard_'+(final_strata_vars.split(','))[i]+'.json').put(Body= jsonBuffer.getvalue())

ttest_info=pd.DataFrame(columns=["variable", "average target","average control","p-value", "F","comment"])
def mean_test_2grps(var):
     print('***** The averages of are:\n')
     averages=final_tab.groupby('group').agg({var:'mean'})
     avegare_target=averages.iloc[1,0]
     aveage_control=averages.iloc[0,0]
     print(final_tab.groupby('group').agg({var:'mean'}))
     groups=pd.unique(final_tab.group.values)
     d_data = {grp:final_tab[var][final_tab.group == grp] for grp in groups}
     #is_normal=stats.norm.rvs(d_data['train'], d_data['test'])
     F, p = stats.f_oneway(d_data['group1'], d_data['group2'])
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
     F2, p2 = stats.kruskal(d_data['group1'], d_data['group2'])
     print("p-value for significance is: ", p2)
     print('\n')
     sns.boxplot(x='group', y=var, data=final_tab, palette="Set1")
    
     ttest_info['variable']=var
     ttest_info['average target']=avegare_target
     ttest_info['average control']=aveage_control
     ttest_info['p-value']=p
     ttest_info['F']=F
     ttest_info['comment']=comment 
     return 


data.fillna('NA',inplace=True)

final_strata_vars= final_strata_vars[1:]
    
summary_data=data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})

summary_data.rename(columns={id_variable:'customer_count'},inplace=True)
one_class_tab=pd.DataFrame(summary_data[summary_data['customer_count']==1])


one_class_tab=one_class_tab[final_strata_vars.split(',')+'customer_count'.split(',')]
size=one_class_tab.size
dim=one_class_tab.ndim

shape=one_class_tab.shape #get the number of lines of the table - number of members who are unique in their strata
shape[0]


if shape[0]>0:
    data=pd.merge(data,one_class_tab,on=final_strata_vars.split(','),how='left')
    one_class_tab_details=pd.DataFrame(data[data['customer_count']==1])
    data=pd.DataFrame(data[data['customer_count']!=1])
else:
    print('there is no class/strata with one members')
    
test=data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})


nb_groups
group1_pct
group2_pct
group3_pct

nb_group1=group1_pct*data.shape[0]

test=data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})

tab_train,tab_test= train_test_split(data, test_size=group1_pct, stratify=data[final_strata_vars.split(',')])

if nb_groups==2: #2 groups selection
    tab_train,tab_test= train_test_split(data, test_size=group1_pct, stratify=data[final_strata_vars.split(',')])
    tab_group2=tab_train
    tab_group1=tab_test
    tab_group1['group']='group1'
    tab_group2['group']='group2'
    if one_class_tab.shape[0]>0:
        one_class_tab_details['group']='group1'
        #one_class_tab_details.drop(['members_count'])
        frames=[tab_group1,tab_group2,one_class_tab_details]
    else:
        frames=[tab_group1,tab_group2]

    final_tab=pd.concat(frames)
    final_tab.shape[0]   
  
    for i in range(0,len(select_numeric_vars.split(','))):
        if (select_numeric_vars.split(',')[i])!="":
            var=select_numeric_vars.split(',')[i]#select_numeric_vars.split(',')[1]
            print('***** The averages of are:\n')
            averages=final_tab.groupby('group').agg({var:'mean'})
            avegare_target=averages.iloc[1,0]
            aveage_control=averages.iloc[0,0]
            print(final_tab.groupby('group').agg({var:'mean'}))
            groups=pd.unique(final_tab.group.values)
            d_data = {grp:final_tab[var][final_tab.group == grp] for grp in groups}
            #is_normal=stats.norm.rvs(d_data['train'], d_data['test'])
            F, p = stats.f_oneway(d_data['group1'], d_data['group2'])
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
            F2, p2 = stats.kruskal(d_data['group1'], d_data['group2'])
            print("p-value for significance is: ", p2)
            print('\n')
            sns.boxplot(x='group', y=var, data=final_tab, palette="Set1")
            ttest_info = ttest_info.append({'variable': var,
                                            'average target': avegare_target,
                                            'average control': aveage_control,
                                            'p-value':p,
                                            'F':F,
                                            'comment':comment}, ignore_index=True)   
            jsonBuffer = io.StringIO()
            session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
            s3 = session.resource('s3')
            ttest_info.to_json(jsonBuffer, orient='values');
            s3.Object(bucket, 'control_group_selection/results/dashboard_ttest_2groups.json').put(Body= jsonBuffer.getvalue())
        
elif nb_groups==3:  
    tab_train,tab_test= train_test_split(data, test_size=group1_pct, stratify=data[final_strata_vars.split(',')])
    tab_group1=tab_test
    sub_data=tab_train
    sub_data.drop(columns=['customer_count'],inplace=True)
    
    summary_data=sub_data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})
    summary_data.rename(columns={id_variable:'customer_count'},inplace=True)
    one_class_tab2=pd.DataFrame(summary_data[summary_data['customer_count']==1])
    one_class_tab2=one_class_tab2[final_strata_vars.split(',')+'customer_count'.split(',')]
    size=one_class_tab2.size
    dim=one_class_tab2.ndim
    if one_class_tab2.shape[0]>0:
        sub_data=pd.merge(sub_data,one_class_tab2,on=final_strata_vars.split(','),how='left')
        one_class_tab_details1=pd.DataFrame(sub_data[sub_data['customer_count']==1])
        sub_data=pd.DataFrame(sub_data[sub_data['customer_count']!=1])
    else:
        print('there is no class/strata with one members')
    del tab_train
    del tab_test    
    new_groupe2_pct=round(1-(group2_pct*data.shape[0])/sub_data.shape[0],1)
    tab_train,tab_test= train_test_split(sub_data, test_size=new_groupe2_pct, stratify=sub_data[final_strata_vars.split(',')])
    tab_group2=tab_train
    tab_group3=tab_test
    # for i in range(1,nb_groups):
    #     tab_train,tab_test= train_test_split(data, test_size=group1_pct, stratify=data[final_strata_vars.split(',')])
    tab_group1['group']='group1'
    tab_group2['group']='group2'
    tab_group3['group']='group3'
    if one_class_tab2.shape[0]>0:
        one_class_tab2['group']='group2'
        #one_class_tab_details.drop(['members_count'])
        frames=[tab_group1,tab_group2,tab_group3,one_class_tab2]
    else:
        frames=[tab_group1,tab_group2,tab_group3]
    final_tab=pd.concat(frames)
    final_tab.shape[0]   
    #anova test for 3 groups
    for i in range(0,len(select_numeric_vars.split(','))):
        if (select_numeric_vars.split(',')[i])!="":
            mod=ols(select_numeric_vars.split(',')[i]+' ~ group',data=final_tab).fit()
            aov_table = sm.stats.anova_lm(mod, typ=2)
            print(aov_table)
            mod.summary()
            pair_t = mod.t_test_pairwise('group')
            pair_t.result_frame
            jsonBuffer = io.StringIO()
            session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
            s3 = session.resource('s3')
            aov_table.to_json(jsonBuffer, orient='values');
            s3.Object(bucket, 'control_group_selection/results/dashboard_'+select_numeric_vars.split(',')[i]+'anova.json').put(Body= jsonBuffer.getvalue())
else:
    print("There is no groups")


select_numeric_vars.split(',')
final_numvars= select_numeric_vars.split(',')[1:]
summary_var_cat_list= final_strata_vars.split(',')+['group']

final_tab.fillna('NA',inplace=True)
group_summary=final_tab.groupby(summary_var_cat_list,as_index=False).agg({id_variable:'count'})

for i in range(0,len(final_numvars)):
    grp_sum=final_tab.groupby(summary_var_cat_list,as_index=False).agg({final_numvars[i]:'sum'})
    group_summary=pd.merge(group_summary,grp_sum,on=summary_var_cat_list,how='left')
    
jsonBuffer = io.StringIO()
session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
s3 = session.resource('s3')
group_summary.to_json(jsonBuffer, orient='values');
s3.Object(bucket, 'control_group_selection/results/dashboard_group_summary.json').put(Body= jsonBuffer.getvalue())

#### export  results -----------------------------------------
groups_selection_tab=final_tab[['CustomerID','group']]
jsonBuffer = io.StringIO()
session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
s3 = session.resource('s3')
groups_selection_tab.to_json(jsonBuffer, orient='values');
s3.Object(bucket, 'control_group_selection/output/group_selection.json').put(Body= jsonBuffer.getvalue())
    