import xarray as xr
import pandas as pd
import numpy as np

def transform_spartacus_daily(df):
    df['Doy'] = df['time'].dt.day_of_year
    df['TAir'] = df[['Tn [degree_Celsius]', 'Tx [degree_Celsius]']].mean(axis=1)
    df = df[['Doy','RR [kg m-2]','TAir','lat','lon']].copy()
    df.rename(columns = {'RR [kg m-2]':'Precip'}, inplace = True)
    return df

def transform_inca_hourly(df):
    df = calculate_daily_means_and_sums_from_hourly(df)
    df = add_vpd(df)
    df = lat_lon_to_end(df)
    df = df.rename(columns={"RR [kg m-2]": "RRSUM [kg m-2]"})
    return df

def write_df_to_csv(df, file, index=True):
    df.to_csv(file, index=index)

def calculate_daily_means_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=False)
    df = grouped.resample('d', on='time').apply(lambda x: np.mean(x.values))
    df.reset_index(level=[0],inplace=True)
    df.drop(["level_0"], axis=1, inplace=True)
    return df

def calculate_daily_sums_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=False)
    df = grouped.resample('d', on='time').apply(lambda x: np.sum(x.values))
    df.reset_index(level=[0],inplace=True)
    df.drop(["level_0"], axis=1, inplace=True)
    return df

def calculate_daily_means_and_sums_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=True)
    df = grouped.resample('d', on='time').agg(
        {"GL [W m-2]":'mean',"RH2M [percent]":'mean',"T2M [degree_Celsius]":'mean', "RR [kg m-2]":'sum'})
    # df = grouped.resample('d', on='time').agg({"RR [kg m-2]":'sum'}).dropna(how='all')
    df.reset_index(level=['lon'],inplace=True)
    df.reset_index(level=['lat'],inplace=True)
    lat_lon_to_end(df)

    # df.drop(["level_0"], axis=1, inplace=True)
    return df

def lat_lon_to_end(df):
    lat = df[['lat']]
    lon = df[['lon']]
    df.drop(['lat'],axis=1,inplace=True)
    df.drop(['lon'],axis=1,inplace=True)
    df['lat'] = lat
    df['lon'] = lon
    return df

def calculate_vpd(row):
    tair = row['T2M [degree_Celsius]']
    rh = row['RH2M [percent]']
    svp = 610.7 * 10**(7.5*tair/(237.3+tair))
    vpd = svp * (1-(rh/100)) / 1000
    return vpd

def add_vpd(df):
    df['VPD [kPA]'] = df.apply(calculate_vpd,axis=1)
    return df

def vpd(tair,rh):
    svp = 610.7 * 10**(7.5*tair/(237.3+tair))
    vpd = svp * (1-(rh/100)) / 1000
    return vpd