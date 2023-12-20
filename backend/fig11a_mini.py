#!/usr/bin/env python
# coding: utf-8

# In[25]:


import numpy as np
import pandas as pd
from collections import namedtuple, Counter

import copy
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


# In[26]:


def random_logit(x):
    z = 1.0 / (1 + np.exp(-x))
    # print(z)
    s = np.random.binomial(n=1, p=z)

    return s


def roundlst(x):
    l = []
    for v in x:
        if v > 0.5:
            l.append(1)
        else:
            l.append(0)
    return l


def roundl(x, th):
    l = []
    for v in x:
        if v > th:
            l.append(1)
        else:
            l.append(0)
    return l


def roundl4(x, th):
    l = []
    for v in x:
        if v <= th:
            l.append(0)
        elif v <= 2 * th:
            l.append(1)
        elif v <= 3 * th:
            l.append(2)
        else:  # v<=4*th:
            l.append(3)
    return l


# In[ ]:


# In[27]:


def get_data(N, seed):
    # N=10000
    np.random.seed(seed)
    S = np.random.binomial(n=1, p=0.5, size=N)
    A = np.random.binomial(n=2, p=0.5, size=N)
    noise1 = np.random.binomial(n=2, p=0.05, size=N)
    noise2 = np.random.binomial(n=2, p=0.05, size=N)
    noise3 = np.random.binomial(n=2, p=0.05, size=N)
    noise4 = np.random.binomial(n=2, p=0.05, size=N)
    St = np.array(roundl((2 * S + A + noise1) / 2, 1))

    Cred = np.array(roundl((0.5 * S + 1.5 * A + noise1) / 2, 1))

    sav = np.array(roundl((S + A + noise2) / 3, 0.5))

    hous = np.array(roundl((S + noise3) / 2, 0.5))

    # X1 = (2*S+A+np.random.normal(loc=0.0, scale=0.2, size=N))#(np.random.normal(loc=100.0, scale=1.16, size=N)) # N(0,1)
    # X2 =(3*A+2*S+np.random.normal(loc=0.0, scale=0.2, size=N))#random_logit(100*X1)#+np.random.normal(loc=0.0, scale=0.16, size=N)
    # Y = random_logit((A+3*St+2*sav+hous)/50)
    Y = roundlst((St / 3 + sav / 3 + hous / 3 + noise4))
    df = pd.DataFrame(S, columns=["S"])
    df_U = pd.DataFrame(S, columns=["S"])
    df_U["noise1"] = noise1
    df_U["noise2"] = noise2
    df_U["noise3"] = noise3
    df_U["noise4"] = noise4
    df["A"] = A
    df["S"] = S
    df["St"] = St
    df["Cred"] = Cred
    df["sav"] = sav
    df["hous"] = hous
    df["Y"] = Y

    return (df, df_U)


def causal_effect(dolst, df, df_U):
    N = df.shape[0]
    if "S" in dolst.keys():
        S = np.array([dolst["S"]] * df.shape[0])  # Construct a list of same size as df
    else:
        S = df["S"]

    if "A" in dolst.keys():
        A = np.array([dolst["A"]] * df.shape[0])  # Construct a list of same size as df
    else:
        A = df["A"]

    noise1 = df_U["noise1"]
    noise2 = df_U["noise2"]
    noise3 = df_U["noise3"]
    noise4 = df_U["noise4"]
    if "St" in dolst.keys():
        St = np.array([dolst["St"]] * df.shape[0])
    elif "A" in dolst.keys() or "S" in dolst.keys():
        St = np.array(roundl((2 * S + A + noise1) / 2, 1))
    else:
        St = df["St"]

    if "sav" in dolst.keys():
        sav = np.array([dolst["sav"]] * df.shape[0])
    elif "A" in dolst.keys() or "S" in dolst.keys():
        sav = np.array(roundl((S + A + noise2) / 3, 0.5))
    else:
        sav = df["sav"]

    if "hous" in dolst.keys():
        hous = np.array([dolst["hous"]] * df.shape[0])
    elif "A" in dolst.keys() or "S" in dolst.keys():
        hous = np.array(roundl((S + noise3) / 2, 0.5))
    else:
        hous = df["hous"]

    if "Cred" in dolst.keys():
        Cred = np.array([dolst["Cred"]] * df.shape[0])
    elif "A" in dolst.keys() or "S" in dolst.keys():
        Cred = np.array(roundl((0.5 * S + 1.5 * A + noise1) / 2, 1))
    else:
        Cred = df["Cred"]

    # print (St)
    # X1 = (2*S+A+np.random.normal(loc=0.0, scale=0.2, size=N))#(np.random.normal(loc=100.0, scale=1.16, size=N)) # N(0,1)
    # X2 =(3*A+2*S+np.random.normal(loc=0.0, scale=0.2, size=N))#random_logit(100*X1)#+np.random.normal(loc=0.0, scale=0.16, size=N)
    # Y = random_logit((A+3*St+2*sav+hous)/50)
    Y = roundlst((St / 3 + sav / 3 + hous / 3 + noise4))
    df = pd.DataFrame(np.array(list(S)), columns=["S"])

    df["A"] = np.array(list(A))
    # print(df)
    df["S"] = np.array(list(S))
    df["St"] = np.array(list(St))
    df["sav"] = np.array(list(sav))
    df["hous"] = np.array(list(hous))
    df["Cred"] = np.array(list(Cred))
    df["Y"] = np.array(list(Y))

    return df
    # For each variable in dolst, change their descendants


# In[ ]:


# In[ ]:


# In[28]:


# In[ ]:


# In[29]:


from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_regression

debug = False


def get_combination(lst, tuplelst):
    i = 0
    new_tuplelst = []
    if len(tuplelst) == 0:
        l = lst[0]
        for v in l:
            new_tuplelst.append([v])
        if len(lst) > 1:
            return get_combination(lst[1:], new_tuplelst)
        else:
            return new_tuplelst

    currlst = lst[0]
    for l in tuplelst:
        for v in currlst:
            newl = copy.deepcopy(l)
            newl.append(v)
            new_tuplelst.append(newl)

    if len(lst) > 1:
        return get_combination(lst[1:], new_tuplelst)
    else:
        return new_tuplelst


def get_C_set(df, C):
    lst = []
    for Cvar in C:
        lst.append(list(set(list(df[Cvar]))))

    combination_lst = get_combination(lst, [])

    return combination_lst


def get_val(row, target, target_val):
    i = 0
    while i < len(target):
        if not int(float(row[target[i]])) == int(float(target_val[i])):
            return 0
        i += 1
    return 1


def train_regression(df, conditional, conditional_values, target, target_val):
    new_lst = []
    count = 0
    for index, row in df.iterrows():
        new_lst.append(get_val(row, target, target_val))
        if new_lst[-1] == 1:
            count += 1
    if len(conditional) == 0:
        return count * 1.0 / df.shape[0]
    if len(list(set(new_lst))) == 1:
        if new_lst[0] == 1:
            return 1
        else:
            return 0

    if len(conditional) > 0:
        X = df[conditional]
    else:
        X = df
    regr = RandomForestRegressor(random_state=0)
    # regr = LogisticRegression(random_state=0)
    regr.fit(X.values, new_lst)
    return regr


def train_regression_raw(df, conditional, conditional_values, AT):
    new_lst = []
    count = 0
    """
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
    """
    if len(conditional) > 0:
        X = df[conditional]
    else:
        X = df
    # regr = RandomForestRegressor(random_state=0)
    regr = LinearRegression()  # random_state=0)

    regr.fit(X, df[AT])
    return regr


def get_prob_o_regression(df, conditional, conditional_values, target, target_val):
    new_lst = []
    count = 0
    for index, row in df.iterrows():
        new_lst.append(get_val(row, target, target_val))
        if new_lst[-1] == 1:
            count += 1
    if len(conditional) == 0:
        return count * 1.0 / df.shape[0]
    if len(list(set(new_lst))) == 1:
        if new_lst[0] == 1:
            return 1
        else:
            return 0

    if len(conditional) > 0:
        X = df[conditional]
    else:
        X = df
    start = time.process_time()

    regr = RandomForestRegressor(random_state=0)

    # regr = LogisticRegression(random_state=0)
    regr.fit(X.values, new_lst)
    # print("timesssssssss",time.process_time() - start)

    # print (regr.coef_.tolist())
    # print (regr.predict_proba([conditional_values]),"ASDFDS")
    return regr.predict([conditional_values])[0]
    # return(regr.predict_proba([conditional_values])[0][1])


# In[30]:


def check_g_Ac(row, g_Ac_lst):
    i = 0
    for g_attr_lst in g_Ac_lst:
        if "*" in g_attr_lst:
            return True
        found = True
        for attr, attrval in g_attr_lst:
            if row[attr] == attrval:
                continue
            else:
                found = True
                break
        if found:
            return True
    return False


# In[31]:


import time


def get_query_output(
    df,
    q_type,
    AT,
    prelst,
    prevallst,
    postlst,
    postvallst,
    Ac,
    c,
    g_Ac_lst,
    interference,
    blocks,
):
    # interference is set of attributes of other tuples in a block that affect current tuple's attribute
    # blocks are list of lists

    # Identify all attributes which are used for regression and add as columns

    # print (len(sub_df),len(sub_intervene))
    if q_type == "count":
        conditioning_set = prelst
        #        intervention=
        backdoorlst = []
        # for attr in Ac:
        #     backdoorlst.extend(backdoor[attr])
        backdoorlst = list(set(backdoorlst))
        if len(backdoorlst) > 0:
            backdoorvals = get_C_set(df, backdoorlst)
            # print(backdoorvals)
        else:
            backdoorvals = []
            return get_prob_o_regression(df, Ac, c, postlst, postvallst)
        total_prob = 0
        regr = ""
        iter = 0
        for backdoorvallst in backdoorvals:
            conditioning_set = []
            conditioning_set.extend(prelst)
            conditioning_set.extend(Ac)
            conditioning_set.extend(backdoorlst)

            conditioning_val = []
            conditioning_val.extend(prevallst)
            conditioning_val.extend(c)
            conditioning_val.extend(backdoorvallst)

            # print ("conditioning set",conditioning_set,conditioning_val)
            # print("post condition",postlst,postvallst)
            if iter == 0:
                start = time.process_time()

                regr = train_regression(
                    df, conditioning_set, conditioning_val, postlst, postvallst
                )
                # print("time",time.process_time() - start)
            # print (conditioning_val)
            pogivenck = regr.predict([conditioning_val])[
                0
            ]  # (get_prob_o_regression(df,conditioning_set,conditioning_val,postlst,postvallst))
            # print("this",prelst,prevallst,backdoorlst,backdoorvallst)
            pcgivenk = get_prob_o_regression(
                df, prelst, prevallst, backdoorlst, backdoorvallst
            )
            # print (pogivenck,pcgivenk)
            total_prob += pogivenck * pcgivenk
            iter += 1

        print("final prob is ", total_prob)
        # print (iter)
        return total_prob
    if q_type == "avg":
        conditioning_set = prelst
        #        intervention=
        backdoorlst = []
        # for attr in Ac:
        #     backdoorlst.extend(backdoor[attr])
        backdoorlst = list(set(backdoorlst))
        if len(backdoorlst) > 0:
            backdoorvals = get_C_set(df, backdoorlst)
            print(backdoorvals)
        else:
            backdoorvals = [[]]
        total_prob = 0
        regr = ""
        iter = 0
        print(backdoorvals)

        for backdoorvallst in backdoorvals:
            conditioning_set = []
            conditioning_set.extend(prelst)
            conditioning_set.extend(Ac)
            conditioning_set.extend(backdoorlst)

            conditioning_val = []
            conditioning_val.extend(prevallst)
            conditioning_val.extend(c)
            conditioning_val.extend(backdoorvallst)

            # print ("conditioning set",conditioning_set,conditioning_val, AT)
            if iter == 0:
                regr = train_regression_raw(df, conditioning_set, conditioning_val, AT)
            pogivenck = regr.predict([conditioning_val])[
                0
            ]  # (get_prob_o_regression(df,conditioning_set,conditioning_val,postlst,postvallst))
            # print("this",prelst,prevallst,backdoorlst,backdoorvallst)
            pcgivenk = get_prob_o_regression(
                df, prelst, prevallst, backdoorlst, backdoorvallst
            )
            # print (pogivenck,pcgivenk)
            total_prob += pogivenck * pcgivenk
            iter += 1

        # print("final prob is ",total_prob)
        return total_prob


# # In[32]:


# backdoor = {
#     "S": [],
#     "A": [],
#     "St": ["S", "A"],
#     "sav": ["S", "A"],
#     "hous": ["S", "A"],
#     "Cred": ["S", "A"],
# }


# # In[33]:


# # In[34]:


# import time


# scores = {}
# times = {}
# sampled_times = {}
# for size in [10000, 100000, 200000, 400000, 600000, 800000, 1000000]:
#     (orig_df, df_U) = get_data(size, 0)

#     print(size)
#     times[size] = []
#     sampled_times[size] = []

#     for col in ["St", "hous", "sav", "Cred", "S"]:
#         start = time.time()
#         score = get_query_output(
#             orig_df, "count", "", [], [], ["Y"], [1], [col], [1], ["*"], "", {}
#         )
#         end = time.time()
#         times[size].append(end - start)

#         start = time.time()
#         df = orig_df.sample(n=10000, random_state=0)
#         score = get_query_output(
#             df, "count", "", [], [], ["Y"], [1], [col], [1], ["*"], "", {}
#         )
#         end = time.time()
#         sampled_times[size].append(end - start)

# print(times)
# print(sampled_times)


# # In[35]:


# df


# # In[36]:


# backdoor = {"S": [], "A": [], "St": [], "sav": [], "hous": [], "Cred": []}

# indep_times = {}
# for size in [10000, 100000, 200000, 400000, 600000, 800000, 1000000]:
#     (orig_df, df_U) = get_data(size, 0)

#     feat = list(df.columns)
#     indep_times[size] = []

#     for col in ["St", "hous", "sav", "Cred", "S"]:
#         start = time.time()
#         score = get_query_output(
#             df=orig_df,
#             q_type="count",
#             AT="",
#             prelst=[],
#             prevallst=[],
#             postlst=["Y"],
#             postvallst=[1],
#             Ac=[col],
#             c=[1],
#             g_Ac_lst=["*"],
#             interference="",
#             blocks={},
#         )
#         end = time.time()
#         indep_times[size].append(end - start)
