# -*- coding: utf-8 -*-
"""
Created on Sat Jan 15 15:58:53 2022

@author: asheesh janda
"""

# 1. Clean the functions
# 2. Make it production ready
# 3. Make it modular
# Evaluate_IV
# Is_Coarse_Class
# Coarse_Class
# Create_Dummies

import pandas as pd
import numpy as np
import logging 



logging.basicConfig(level=logging.DEBUG)

def Evaluate_IV_new(inputs_,outputs_):
    
    
    inputs_.reset_index(drop=True,inplace=True)
    outputs_.reset_index(drop=True,inplace=True)
    try:
        assert (isinstance(inputs_,pd.core.series.Series) and
                isinstance(outputs_,pd.core.series.Series)), 'ERROR: Must provide series input'
        logging.info('SUCCESS: input type crieteria satisfied')
    except AssertionError:
        logging.error('ERROR: accepts only series inputs')
        return 0
    if(len(inputs_)!=len(outputs_)):
        raise Exception('ERROR: input and output should be of same length input {} where as output {}'
                        .format(len(inputs_),len(outputs_)))
        return 0
    try:
        assert isinstance (outputs_.tolist()[0],int), 'output should take 1\0 as values'
    except (IndexError,AssertionError):
        raise Exception('ERROR: Output is either empty or does not take 1 or 0')
        return 0
    try:
        assert outputs_.sum()>0,'ERROR : output has no event'
    except AssertionError:
        raise Exception('NO EVENT CAPTURED: Output has no event') 
     
    logging.info('Calulating IV for {} '.format(inputs_.name))
    dt_New = pd.concat([inputs_,outputs_],axis=1)
    df_table = pd.DataFrame(dt_New.groupby([inputs_.name]).
                            agg({outputs_.name:['sum','count']})).reset_index(drop=False)
    df_table.xs(outputs_.name,axis=1,drop_level=True).reset_index(drop=False,inplace=True)
    df_table.columns=[inputs_.name,'goods','total']
    df_table['bads']=df_table['total'] - df_table['goods']
    df_table['total_goods'] = df_table.goods.sum()
    df_table['total_bads'] = df_table.bads.sum()
    df_table.loc[df_table.goods==0,'goods']=0.5
    df_table.loc[df_table.bads==0,'bads']=0.5
    df_table['perc_goods'] = df_table['goods']/df_table['total_goods']
    df_table['perc_bads'] = df_table['bads']/df_table['total_bads']
    df_table['perc_total'] = df_table['total']/df_table['total'].sum()
    df_table['woe'] = df_table['perc_goods']/df_table['perc_bads']
    df_table['woe'] = df_table['woe'].apply(lambda x: np.log(x))
    df_table['perc_diff'] = df_table['perc_goods']-df_table['perc_bads']
    df_table['IV'] = df_table['perc_diff'] * df_table['woe']
    df_table['variable'] = inputs_.name
    df_table.rename(columns={inputs_.name:'level'},inplace=True)
    return(df_table)


	
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def Is_Coarse_Class_New(IV_Category_List):
    try:
        assert isinstance(IV_Category_List,list),'IV calulation issue'
    except AssertionError:
        logging.error('ERROR: IV calculation encountered issue, please check input\output')
        return None
    Coarse_Class = {}
    try:
        coarse_df = [i for i in IV_Category_List if i.shape[0]>5]
    except AttributeError:
        logging.error('ERROR: IV calculation had an issue , provide valid inputs')
        return None
    for df_temp in coarse_df:
        a = df_temp.sort_values('woe')
        Var = df_temp.variable[0]
        step_,Remainder = np.divmod(a.shape[0],5)
        if(Remainder!=0):
            Coarse_Class[Var] = list(chunks(a.level.tolist(), step_+1))
        else:
            Coarse_Class[Var] = list(chunks(a.level.tolist(), step_))
    return(Coarse_Class)


#Identify the Columns which needs to be coarse classed and store the coarse Categories as lists and variable name as key

def Coarse_Class_New(Train_Category,Coarse_Class):
    try:
        assert isinstance (Train_Category,pd.core.frame.DataFrame), 'ERROR: Issues in inputs provided'
    except AssertionError:
        logging.error('ERROR: Input be of type dataframe')
    try:
        assert len(Coarse_Class.keys())>0,'no columns to coarse class'
        Coarse_Class_Cols = list(Coarse_Class.keys())
        df_Coarse_Class = Train_Category[Coarse_Class_Cols]
        for i in Coarse_Class_Cols:
            cnt=1
            for j in Coarse_Class[i]:
                df_Coarse_Class = df_Coarse_Class.apply(pd.Series.replace,to_replace=j,value=str(cnt))
                cnt = cnt+1
        return(df_Coarse_Class)       
    except AssertionError:
        logging.INFO('INFO: Variables <5 levels cannot be coarse classed')
        return None

# Applying Coarse Class to The Categories


def applycoarseclass(data,Y):
    
    if len(data) == 0:
        raise ValueError("Empty data frame provided")
    
    IV_Category_List = []
    Cols_to_Coarse = []
    try:        
        for i in data.columns:
            if(i!=Y):
                get_IV = Evaluate_IV_new(data.loc[:,i],data[Y])
                IV_Category_List.append(get_IV)
            Cols_to_Coarse.append(i)
    except (AttributeError,ValueError):
        print('Expected datafram type, for more information check args expected')
        print("Can't perform coarse Classing")
        return(None,None,None)

    Coarse_Cls = Is_Coarse_Class_New(IV_Category_List)
    df_Coarse_Class = Coarse_Class_New(data,Coarse_Cls)

    Coarse_Columns_IV = [Evaluate_IV_new(df_Coarse_Class.loc[:,i],data[Y]).IV.sum() for i in df_Coarse_Class.columns]
    Coarse_Columns = pd.DataFrame({'Col':df_Coarse_Class.columns.tolist(),'IV':Coarse_Columns_IV})
    Coarse_Columns = Coarse_Columns.loc[Coarse_Columns.IV>0.1,:] 
    # print()
    df_Coarse_Class = df_Coarse_Class[Coarse_Columns.Col]
    data.drop(list(Coarse_Cls.keys()),inplace=True,axis=1)
    data = pd.concat([data,df_Coarse_Class],axis=1)
    x_cols = [i for i in data.columns.tolist() if i!=Y]
    Train_Cat_IV = [Evaluate_IV_new(data.loc[:,i],data[Y]).IV.sum() for i in data[x_cols].columns ]
    Train_Cat_IV= pd.DataFrame({'Col':data[x_cols].columns.tolist(),'IV':Train_Cat_IV})
    # Train_Cat_IV = Train_Cat_IV.loc[Train_Cat_IV.IV>0.3,:]
    data = data[Train_Cat_IV.Col]
    return(data,Coarse_Cls,Train_Cat_IV)




