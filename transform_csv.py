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
        {"GL [W m-2]":lambda x: np.sum(x.values),
        "RH2M [percent]": lambda x: np.mean(x.values),
        "T2M [degree_Celsius]": lambda x: np.mean(x.values), 
        "RR [kg m-2]": lambda x: np.sum(x.values)})
    df.reset_index(level=['lon'],inplace=True)
    df.reset_index(level=['lat'],inplace=True)
    lat_lon_to_end(df)
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

def calculate_vpd_clipick(row):
    tair = row['TAir']
    rh = row['RH']
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

def clipick_index_to_datetime(df):
    df.index = pd.to_datetime(df[['Day','Month','Year']])
    df.drop(columns=['Day','Month','Year'], inplace=True)
    return df

def calculate_par(row):
    rss = row['rss']
    par = rss *0.44*4.56
    return par

def add_value(df,column_name,function):
    df[column_name] = df.apply(function, axis=1)
    return df


def transform_clipick(df):
    df['TAir'] = df[['tasmax', 'tasmin']].mean(axis=1)
    df['RH'] = df[['hursmax', 'hursmin']].mean(axis=1)
    df = add_value(df, 'PAR', calculate_par)
    df = add_value (df, 'VPD', calculate_vpd_clipick)
    df = df.rename(columns={"pr": "Precip"})
    df = df[['TAir', 'RH', 'PAR', 'VPD', 'Precip']]
    return df