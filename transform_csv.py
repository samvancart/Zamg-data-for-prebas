import xarray as xr
import pandas as pd
import numpy as np

def transform_spartacus_daily(df):
    df.index = df['time']
    df['Doy'] = df['time'].dt.day_of_year
    df['TAir'] = df[['Tn [degree_Celsius]', 'Tx [degree_Celsius]']].mean(axis=1)
    df = df[['Doy','RR [kg m-2]','TAir','lat','lon']].copy()
    df = df.rename(columns = {'RR [kg m-2]':'Precip'})
    return df

def transform_inca_hourly(df):
    df = calculate_daily_means_and_sums_from_hourly(df)
    df = add_value(df, 'VPD', calculate_vpd)
    df = add_value(df, 'RSS', convert_gl_to_rss)
    df = lat_lon_to_end(df)
    # df = df.rename(columns={"RR [kg m-2]": "RRSUM [kg m-2]"})
    df.drop(['GL [W m-2]'],axis=1,inplace=True)
    df = df.rename(columns={"RR [kg m-2]": "Precip"})
    df = df.rename(columns={"T2M [degree_Celsius]": "TAir"})
    df = df.rename(columns={"RH2M [percent]": "RH"})
    return df

def rename_all_columns(df, name):
    for col_name in df.columns:
        if col_name != 'time':
            df = df.rename(columns={col_name: f'{col_name} {name}'})
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
    df.index.name = 'time'
    df.drop(columns=['Day','Month','Year'], inplace=True)
    return df

def calculate_par(row):
    rss = row['rss']
    par = rss *0.44*4.56
    return par

def add_value(df,column_name,function):
    df[column_name] = df.apply(function, axis=1)
    return df

# USING FORMULA: 1 W/m2 = 0.0864 MJ/m2/day. SAME AS 60*60*24*(W/m-2)/1000000 = MJ/m-2/day
def convert_gl_to_rss(row):
    conversion = 0.0864
    gl  = row['GL [W m-2]']
    rss = gl*conversion
    return rss 

def transform_clipick(df):
    df = df.astype(float)
    df['TAir'] = df[['tasmax', 'tasmin']].mean(axis=1)
    df['RH'] = df[['hursmax', 'hursmin']].mean(axis=1)
    df = add_value(df, 'PAR', calculate_par)
    df = add_value (df, 'VPD', calculate_vpd_clipick)
    df = df.rename(columns={'pr': 'Precip'})
    df = df.rename(columns={'rss': 'RSS'})
    df = df[['TAir', 'RH', 'PAR', 'VPD', 'Precip', 'RSS']]
    return df

def transform_csv_to_plottable(df_name, column_name, from_file):
    df = pd.read_csv(from_file, parse_dates=['time'])
    df = df[['time', column_name]].copy()
    df = df.rename(columns = {column_name:f'{column_name} {df_name}'})
    df['time'] = df['time'].dt.date
    return df

def transform_df_to_plottable(df, df_name, column_name):
    df = df[['time', column_name]].copy()
    df = df.rename(columns = {column_name:f'{column_name} {df_name}'})
    df['time'] = df['time'].dt.date
    return df

def transform_time_to_dt_date(df):
    df['time'] = df['time'].dt.date
    return df

def merge_dfs(df1,df2):
    df = pd.merge_ordered(df1, df2, on="time").fillna(np.nan)
    return df