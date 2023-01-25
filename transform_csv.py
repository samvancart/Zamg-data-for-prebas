import xarray as xr
import pandas as pd
import numpy as np

def transform_spartacus_daily(df):
    df['Doy'] = df['time'].dt.day_of_year
    df['TAir'] = df[['Tn [degree_Celsius]', 'Tx [degree_Celsius]']].mean(axis=1)
    df = df[['Doy','RR [kg m-2]','TAir','lat','lon']].copy()
    df.rename(columns = {'RR [kg m-2]':'Precip'}, inplace = True)
    return df

def calculate_daily_averages_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=False)
    df = grouped.resample('d', on='time').mean().dropna(how='all')
    df.reset_index(level=[0],inplace=True)
    df.drop(["level_0"], axis=1, inplace=True)
    return df

def calculate_daily_sums_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=False)
    df = grouped.resample('d', on='time').sum().dropna(how='all')
    df.reset_index(level=[0],inplace=True)
    df.drop(["level_0"], axis=1, inplace=True)
    return df

def daily_means_and_sums_from_hourly(df):
    grouped = df.groupby(["lat", "lon"],as_index=True)
    df = grouped.resample('d', on='time').agg(
        {"GL [W m-2]":'mean',"RH2M [percent]":'mean',"T2M [degree_Celsius]":'mean', "RR [kg m-2]":'sum'}).dropna(
            how='all')
    # df = grouped.resample('d', on='time').agg({"RR [kg m-2]":'sum'}).dropna(how='all')
    df.reset_index(level=['lon'],inplace=True)
    df.reset_index(level=['lat'],inplace=True)
    lat = df[['lat']]
    lon = df[['lon']]
    df.drop(['lat'],axis=1,inplace=True)
    df.drop(['lon'],axis=1,inplace=True)
    df['lat'] = lat
    df['lon'] = lon
    
    # df.drop(["level_0"], axis=1, inplace=True)
    return df

def calculate_vpd(row):
    TAir = row['T2M [degree_Celsius]']
    RH = row['RH2M [percent]']
    svp = 610.7 * 10**(7.5*TAir/(237.3+TAir))
    vpd = svp * (1-(RH/100)) / 1000
    return vpd

def add_vpd(df):
    df['VPD [kPA]'] = df[['T2M [degree_Celsius]', 'RH2M [percent]']].apply(calculate_vpd,axis=1)
    return df

def vpd(tair,rh):
    svp = 610.7 * 10**(7.5*tair/(237.3+tair))
    vpd = svp * (1-(rh/100)) / 1000
    return vpd