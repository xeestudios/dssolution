# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
from scipy import stats
import csv
import matplotlib.pyplot as plt
import matplotlib.path as path
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta,date
from sklearn.model_selection import KFold, cross_val_score, train_test_split
import boto3
import io 
import statsmodels.api as sm
from statsmodels.formula.api import ols
import sys
import json


#-----------------Paremeters---------------

# params = json.loads(sys.argv[1])

# nb_groups = params['nb_groups']
# group1_pct = params['group1_pct']
# group2_pct = params['group2_pct']
# group3_pct = params['group3_pct']
# stratification_var0 = params['st_var0']
# stratification_var1 = params['st_var1']
# stratification_var2 = params['st_var2']
# stratification_var3 = params['st_var3']
# stratification_var4 = params['st_var4']
# stratification_var5 = params['st_var5']
# stratification_var6 = params['st_var6']
# id_variable = params['id_variable']


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
stratification_var6=''

id_variable='CustomerID'

initial_selected_var_list=stratification_var0+','+stratification_var1+','+stratification_var2+','+stratification_var3+','+stratification_var4+','+stratification_var5+','+stratification_var6

# maximum limit of categories to be used in the stratification.
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
#print(jsonString)
data = pd.read_json(jsonString)
data.head()

#--------------------------
var_types=data.dtypes
Warning_list=[]

if any(data[id_variable].duplicated())==True:
    Warning_list.append('The table has duplicates')
    data=data.drop_duplicates(id_variable)

# print(Warning_list)    
initial_data_size=data.shape[0]

def quantile_func (var,value):
    tab_non_zero=data[data[var]>0]
    quantile_val=tab_non_zero[var].quantile([value]).astype('float64')
    return quantile_val

# convert the numerical variable into ranges and add them to the startification list
final_strata_vars=""
select_numeric_vars=""
counter=0
for i in range(0,len(initial_selected_var_list.split(','))-1):
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

#--------------------export tables for the output dashboard-------------------------------------
count_strata_vars=len(final_strata_vars.split(','))
stat_tab = {}

for i in range(0,count_strata_vars):
    if (final_strata_vars.split(','))[i]!="": 
        stat_tab[i]=data.drop_duplicates(subset=[(final_strata_vars.split(','))[i],id_variable])
        stat_tab[i]=pd.DataFrame(stat_tab[i][(final_strata_vars.split(','))[i]].value_counts().reset_index())
        stat_tab[i].rename(columns={(final_strata_vars.split(','))[i]:'nb_members'},inplace=True)
        stat_tab[i].rename(columns={'index':(final_strata_vars.split(','))[i]},inplace=True)
        
        

# final output to be used thoughout the code

#agregated variable for the bar charts in the dashboard
final_output = {}
for j in range(1,count_strata_vars):
    thisdict = {}
    for col in range(0,stat_tab[j].shape[0]): 
        thisdict[stat_tab[j].iloc[col,0]]=str(stat_tab[j].iloc[col,1])
    
    final_output[final_strata_vars.split(',')[j]] = thisdict

#test for the quantitative variables

ttest_info=pd.DataFrame(columns=["variable", "average target","average control","p-value", "F","comment"])


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
    Warning_list.append('Nb_group(2) - there is no class/strata with one members')
    
    
test=data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})

nb_group1=group1_pct*data.shape[0]

test=data.groupby(final_strata_vars.split(','),as_index=False).agg({id_variable:'count'})

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
            averages=final_tab.groupby('group').agg({var:'mean'})
            avegare_target=averages.iloc[1,0]
            aveage_control=averages.iloc[0,0]
            groups=pd.unique(final_tab.group.values)
            d_data = {grp:final_tab[var][final_tab.group == grp] for grp in groups}
            F, p = stats.f_oneway(d_data['group1'], d_data['group2'])
            if p < 0.05:
                comment="reject null hypothesis"
            else:
                comment="accept null hypothesis"
            F2, p2 = stats.kruskal(d_data['group1'], d_data['group2'])
            sns.boxplot(x='group', y=var, data=final_tab, palette="Set1")
            ttest_info = ttest_info.append({'variable': var,
                                            'average target': avegare_target,
                                            'average control': aveage_control,
                                            'p-value':p,
                                            'F':F,
                                            'comment':comment}, ignore_index=True)   
    #add the ttest table to the final output
    ttest_list=[]
    ttest_list.append(list(ttest_info.head(1)))
    for index, row in ttest_info.iterrows():
        ttest_list.append(list(row))
    final_output['ttest_list']=ttest_list
                
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
        Warning_list.append('Nb_group(3) - there is no class/strata with one members')
    
    del tab_train
    del tab_test    
    
    new_groupe2_pct = round(1-(group2_pct*data.shape[0])/sub_data.shape[0],1)
    tab_train,tab_test = train_test_split(sub_data, test_size=new_groupe2_pct, stratify=sub_data[final_strata_vars.split(',')])
    tab_group2 = tab_train
    tab_group3 = tab_test
    tab_group1['group'] = 'group1'
    tab_group2['group'] = 'group2'
    tab_group3['group'] = 'group3'

    if one_class_tab2.shape[0]>0:
        one_class_tab2['group']='group2'
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
            #print(aov_table)
            mod.summary()
            pair_t = mod.t_test_pairwise('group')
            pair_t.result_frame
            jsonBuffer = io.StringIO()
            session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
            s3 = session.resource('s3')
            aov_table.to_json(jsonBuffer, orient='values');
            s3.Object(bucket, 'control_group_selection/results/dashboard_'+select_numeric_vars.split(',')[i]+'anova.json').put(Body= jsonBuffer.getvalue())            
    #add anova list to the final list
    anova_list=[]
    anova_list.append(list(aov_table.head(1)))
    for index, row in aov_table.iterrows():
        anova_list.append(list(row))
    
    final_output['anova_list'] = anova_list
else:
    Warning_list.append("Group selection - There is no groups")


select_numeric_vars.split(',')
final_numvars= select_numeric_vars.split(',')[1:]
summary_var_cat_list= final_strata_vars.split(',')+['group']

final_tab.fillna('NA',inplace=True)
group_summary=final_tab.groupby(summary_var_cat_list,as_index=False).agg({id_variable:'count'})

for i in range(0,len(final_numvars)):
    grp_sum=final_tab.groupby(summary_var_cat_list,as_index=False).agg({final_numvars[i]:'sum'})
    group_summary=pd.merge(group_summary,grp_sum,on=summary_var_cat_list,how='left')
    
#add the group summary to the final list
group_summary_list=[]
group_summary_list.append(list(group_summary.head(1)))
for index, row in group_summary.iterrows():
    group_summary_list.append(list(row))

final_output['group_summary_list'] = group_summary_list

#prepare the finale data for dashboard-----
final_output['warning_list'] = Warning_list

json=json.dumps(final_output, indent=4) 
print(json)
"""
#### export  results: the below file should be in the user folder with csv format -----------------------------------------
groups_selection_tab=final_tab[['CustomerID','group']]
jsonBuffer = io.StringIO()
session = boto3.Session(aws_access_key_id='AKIA5IM6XOLZZJTX5VPN', aws_secret_access_key='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')
s3 = session.resource('s3')
groups_selection_tab.to_json(jsonBuffer, orient='values');
s3.Object(bucket, 'control_group_selection/output/group_selection.json').put(Body= jsonBuffer.getvalue())
"""