import pandas as pd
import numpy as np


def norm_and_rescale(df1, df1_q, df2_q):
    # NORMALIZE DATA
    df1_norm = get_modified_df(df1, df1_q, get_norm_vals)
    # RESCALE DATA
    df1_rescaled = get_modified_df(df1_norm, df2_q, rescale_vals)
    return df1_rescaled
    

def get_quantile_df(df):
    # GET ALL QUANTILES
    q = df.quantile([.05, .95], numeric_only=True)
    # GET PRECIPITATION QUANTILES FOR NONZERO ONLY
    q_precip = get_nonzero_quantiles(df)
    # REPLACE DF PRECIP QUANTILE
    q['Precip'] = q_precip.values
    # RESET INDEX
    q.reset_index(drop=True, inplace=True)
    return q

# All minus values in column to zero
def minuses_to_zero(df, c='Precip'):
    df[c] = df[c].apply(lambda x: 0 if x<0 else x)
    return df

# Quantiles based only on non zero values
def get_nonzero_quantiles(df,c='Precip',quantile=[.1, .9]):
    mask_new = df[c]
    new = mask_new.where(mask_new>0)
    precip_q = new.quantile(quantile)
    return precip_q

# Insert new values
def get_modified_df(df, series, function):
    """ Replaces original dataframe values with modified ones
    Parameters:
        df (pandas dataframe): dataframe with original values
        series (pandas series): series with new constants for each column in df (names must match df column names)
    Returns:
        dataframe: dataframe with modified values
    """
    mod_d = {}
    for c in df.columns:
        if c in series:
            vals = function(c, df, series)
            mod_d.update({c:vals})
        else:
            mod_d.update({c:df[c]})
    df_mod = pd.DataFrame(data=mod_d)
    return df_mod

# Rescaled values
def rescale_vals(c,df, q):
    min = q.loc[0]
    max = q.loc[1]
    if c == 'Precip':
        vals = df[c].apply(lambda x: (x * (max[c] - min[c]) + min[c]) if x>0 else x)
        return vals
    else:
        vals = (df[c] * (max[c] - min[c]) + min[c])
        return vals
    
# Normalised values
def get_norm_vals(c,df, q):
    min = q.loc[0]
    max = q.loc[1]
    if c == 'Precip':
        vals = df[c].apply(lambda x: (x-min[c])/(max[c]-min[c]) if x>0 else x)
        return vals
    else:
        vals = (df[c]-min[c])/(max[c]-min[c])
        return vals


# Mean of annual sums
def get_combined_annual_mean(df):
    df_annual_pr_sum = get_annual_sums(df)
    return df_annual_pr_sum.mean()


def get_annual_sums(df, value='Precip'):
    grouped = df.groupby(df['time'].dt.year)[value].sum()
    return grouped

def get_annual_means(df, value='Precip'):
    grouped = df.groupby(df['time'].dt.year)[value].mean()
    return grouped

def filter_df_by_date(df, start_date='2011-03-15', end_date='2022-12-31'):
    filtered = df.loc[(df['time'] >= start_date )
                      & (df['time'] <= end_date )]
    return filtered

# Returns deltas for means as series
def get_deltas(df1,df2):
    means1 = df1.mean(numeric_only=True)
    means2 = df2.mean(numeric_only=True)
    delta = means1 - means2
    return delta

# Bias corrected values
def get_bias_vals(c,df,delta):
    if c == 'Precip':
        vals = df[c].apply(lambda x: x+delta[c] if x>0 else x)
        return vals
    else:
        vals = df[c]+delta[c]
        return vals