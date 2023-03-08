import xarray as xr
import pandas as pd
import numpy as np
from netCDF4 import Dataset
from functools import partial


def _preprocess(x, lon_bnds, lat_bnds):
    # Remove unwanted data by coordinates
    ds = x.where((x.lat<lat_bnds[1]) & (x.lat>=lat_bnds[0]) & (x.lon<lon_bnds[1]) & (x.lon>=lon_bnds[0]), drop=True)
    # Return daily means
    return ds.resample(time="1d").mean()

path = "data/net_cdf/t2m/2015/INCAL_HOURLY_T2M"
# path = "data/net_cdf/t2m/2015/INCAL_DAILY_STYRIA_T2M_2015.nc"
# data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# BOX BOUNDARIES
lon_bnds, lat_bnds = (13, 16.7), (46, 47.4)
partial_func = partial(_preprocess, lon_bnds=lon_bnds, lat_bnds=lat_bnds)

# OPEN ALL DATASETS AT ONCE
data = xr.open_mfdataset(
    f"{path}_*.nc", combine='nested', concat_dim='time', preprocess=partial_func
    # f"{path}_201501.nc", combine='nested', concat_dim='time', preprocess=partial_func
)

# CONVERT TO DF
df = data.to_dataframe()
df=df[['T2M','lat','lon']]
new_index=df.index.droplevel(['x', 'y'])
df.set_index(new_index, inplace=True)

# DROP NAN VALUES
df.dropna(inplace=True)

# GROUP BY COORDINATES
grouped = df.groupby(["lat", "lon"],as_index=False)
df = pd.concat([g for _, g in grouped])

# WRITE TO CSV
file = 'data/INCAL_DAILY_T2M_2015_styria_grouped.csv'
df.to_csv(file)
print(df)






