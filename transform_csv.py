import requests
import xarray as xr
import pandas as pd
import numpy as np

file = "data/spartacus-daily/SPARTACUS - Spatial Reanalysis Dataset for Climate in Austria Datensatz_19610101_20221219.csv"
df = pd.read_csv(file, parse_dates=['time'])
# df = pd.read_csv(file)
# print(df)
df['Doy'] = df['time'].dt.day_of_year

df['TAir'] = df[['Tn [degree_Celsius]', 'Tx [degree_Celsius]']].mean(axis=1)
df = df[['Doy','RR [kg m-2]','TAir','lat','lon']].copy()
df.rename(columns = {'RR [kg m-2]':'Precip'}, inplace = True)

# print(df)
# df.to_csv("data/test.csv")
