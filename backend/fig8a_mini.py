#!/usr/bin/env python
# coding: utf-8



import numpy as np
import pandas as pd
from collections import namedtuple, Counter

import copy
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_regression

backdoor = {}

def set_backdoor(new_backdoor):
    globals()['backdoor'] = new_backdoor

def get_backdoor():
    return backdoor
     
        
debug=False
def get_combination(lst,tuplelst):
    i=0
    new_tuplelst=[]
    if len(tuplelst)==0:
        l=lst[0]
        for v in l:
            new_tuplelst.append([v])
        if len(lst)>1:
            return get_combination(lst[1:],new_tuplelst)
        else:
            return new_tuplelst
    

    currlst=lst[0]
    for l in tuplelst:
        
        for v in currlst:
            newl=copy.deepcopy(l)
            newl.append(v)
            new_tuplelst.append(newl)
        
    if len(lst)>1:
        return get_combination(lst[1:],new_tuplelst)
    else:
        return new_tuplelst
    
def get_C_set(df,C):
    lst=[]
    for Cvar in C:
        lst.append(list(set(list(df[Cvar]))))
        
    combination_lst= (get_combination(lst,[]))
    
    return combination_lst


def get_val(row,target,target_val):
    i=0
    while i<len(target):
        if not int(row[target[i]])==int(target_val[i]):
            return 0
        i+=1
    return 1
def train_regression(df,conditional,conditional_values,target,target_val):
    new_lst=[]
    count=0
    for index,row in df.iterrows():
        new_lst.append(get_val(row,target,target_val))
        if new_lst[-1]==1:
            count+=1
    if len(conditional)==0:
        return count*1.0/df.shape[0]
    if len(list(set(new_lst)))==1:
        if new_lst[0]==1:
            return 1
        else:
            return 0
        
    if len(conditional)>0:
        X=df[conditional]
    else:
        X=df
    regr = RandomForestRegressor(random_state=0)
    #regr = LogisticRegression(random_state=0)
    regr.fit(X.values, new_lst)
    return regr
def get_prob_o_regression(df,conditional,conditional_values,target,target_val):
    new_lst=[]
    count=0
    for index,row in df.iterrows():
        new_lst.append(get_val(row,target,target_val))
        if new_lst[-1]==1:
            count+=1
    if len(conditional)==0:
        return count*1.0/df.shape[0]
    if len(list(set(new_lst)))==1:
        if new_lst[0]==1:
            return 1
        else:
            return 0
        
    if len(conditional)>0:
        X=df[conditional]
    else:
        X=df
    regr = RandomForestRegressor(random_state=0)
    #regr = LogisticRegression(random_state=0)
    regr.fit(X.values, new_lst)
    #print (regr.coef_.tolist())
    #print (regr.predict_proba([conditional_values]),"ASDFDS")
    return (regr.predict([conditional_values])[0])
    #return(regr.predict_proba([conditional_values])[0][1])




# In[5]:


def check_g_Ac(row,g_Ac_lst):
    i=0
    for g_attr_lst in g_Ac_lst:
        if '*' in g_attr_lst:
            return True
        found=True
        for (attr,attrval) in g_attr_lst:
            if row[attr] == attrval:
                continue
            else:
                found=True
                break
        if found:
            return True
    return False


def get_query_output(df,q_type,AT,prelst,prevallst,postlst,postvallst,Ac,c,g_Ac_lst,interference, blocks):
    """
    Run what-if queries equivalent to a SQL-like query \\
    e.g. In `Use D Update(B)=b OutputCount (Credit=Good) ForPre (status) = 3.0 ` \\
    df = D; q_type = 'COUNT'; AT = any;
    prelst=[]; prevallst = [] \\
    postlst = ['credit']; postvallst=[1] \\ 
    Ac='status'; c = 3.0 \\
    g_Ac_lst = ['*']; interference='', blocks={}


    
    Args:
        df (pandas.DataFrame): Original Data Frame
        q_type (str): Query type. e.g. 'COUNT'
        AT (str): ?
        prelst (list[str]): List condition list
        prevallst (list[str]): Condition value 
        postlst (_type_): List of target column's name 
        postvallst (_type_): List of target column's value
        Ac (list[str]): List of attribute column's name to change
        c (list[any]): List of values the attribute is hypothetically changing to
        g_Ac_lst (list[str]): List of ??
        interference (str): ?? interference is set of attributes of other tuples in a block that affect current tuple's attribute ??
        blocks (dict): ??

    Returns:
        _type_: _description_
    """
    #interference is set of attributes of other tuples in a block that affect current tuple's attribute
    #blocks are list of lists
    
    #Identify all attributes which are used for regression and add as columns 
    #New columns will be 
    new_df=[]
    newvars=[]
    for var in Ac:
        if var in interference:
            newvars.extend(backdoor[var])
        else:
            newvars.extend([var])
        
    
    for index,row in df.iterrows():
        if index in blocks.keys():
            sameblockelem=blocks[index]
        else:
            sameblockelem=[]
        
        #identify backdoor from other records and add those
        #In interference is not in Ac then interference is enough
        #else we need backdoor of intervened and interference    
        
        for var in newvars:
            iter=0
            #print(var,newvars)
            row["new"+var]=0
            for sibling in sameblockelem:
                row["new"+var]+=df.iloc[sibling][var]
                #assumes A_c is a unique attribute. TODO: change to consider list
                if sibling in g_Ac_lst:
                    row[str(iter)+Ac] = c
                else:
                    row[str(iter)+Ac] = df.iloc[sibling][Ac]
                iter+=1
            if len(sameblockelem) >0:
                row["new"+var]/=len(sameblockelem)
                #We can add interference for all in blocks too
        new_df.append(row)
            
    
    df=pd.DataFrame(new_df)
            
    #print (len(sub_df),len(sub_intervene))
    if q_type=='count':
        conditioning_set=prelst
        #        intervention=
        backdoorlst=[]
        for attr in Ac:
            backdoorlst.extend(backdoor[attr])
        backdoorlst=list(set(backdoorlst))
        if len(backdoorlst)>0:
            backdoorvals=get_C_set(df,backdoorlst)
            print(backdoorvals)
        else:
            backdoorvals=[]
        total_prob=0
        regr=''
        iter=0
        for backdoorvallst in backdoorvals:
            conditioning_set=[]
            conditioning_set.extend(prelst)
            conditioning_set.extend(Ac)
            conditioning_set.extend(backdoorlst)

            conditioning_val=[]
            conditioning_val.extend(prevallst)
            conditioning_val.extend(c)
            conditioning_val.extend(backdoorvallst)

            #print ("conditioning set",conditioning_set,conditioning_val)
            #print("post condition",postlst,postvallst)
            if iter==0:
                regr=train_regression(df,conditioning_set,conditioning_val,postlst,postvallst)
            pogivenck= regr.predict([conditioning_val])[0]#(get_prob_o_regression(df,conditioning_set,conditioning_val,postlst,postvallst))
            
            
            print(prelst,prevallst,backdoorlst,backdoorvallst)
            pcgivenk = (get_prob_o_regression(df,prelst,prevallst,backdoorlst,backdoorvallst))
            print (pogivenck,pcgivenk)
            total_prob+=pogivenck * pcgivenk
            iter+=1
            
        print("final prob is ",total_prob)
        return total_prob
