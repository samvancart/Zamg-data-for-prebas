import xarray as xr
import pandas as pd
import numpy as np
from netCDF4 import Dataset
from functools import partial
from math import radians, cos, sin, asin, sqrt



def _preprocess(x, lon_bnds, lat_bnds):
    # Configure variable names
    coords = list(x.coords)
    ds = x
    if 'lon' in coords or 'lat' in coords:
        ds = ds.rename_vars({'lon':'longitude', 'lat':'latitude'})
    # Remove unwanted data by coordinates
    ds = ds.where((ds.latitude<=lat_bnds[1]) & (ds.latitude>=lat_bnds[0]) & (ds.longitude<=lon_bnds[1]) & (ds.longitude>=lon_bnds[0]), drop=True)
    # Remove unwanted years
    ds = ds.where((ds['time.year']<2012),drop=True)
    # Return daily means
    # return ds.resample(time="1d").mean()
    return ds


# HAVERSINE DISTANCE
def dist(lat1, long1, lat2, long2):
    """
    Replicating the same formula as mentioned in Wiki
    """
    # convert decimal degrees to radians 
    lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km

# FIND NEAREST COORDINATES TO GIVEN COORDINATES IN A DATAFRAME 
def find_nearest_coords(df, lat, long):
    distances = df.apply(
        lambda row: dist(lat, long, row['lat'], row['lon']), 
        axis=1)
    return df.loc[distances.idxmin()]



# CONVERT TO DF
def convert_copernicus_to_df(dataset):
    df = dataset.to_dataframe()
    df.reset_index(inplace=True)
    df.set_index(df['time'], inplace=True)
    df=df[['tg','latitude','longitude']]
    df.rename(columns={'latitude':'lat', 'longitude':'lon'}, inplace=True)
    return df

# TRANSFORM DATAFRAME
def transform_df(df, columns, rename_cols):
    df.reset_index(inplace=True)
    df.set_index(df['time'], inplace=True)
    df=df[columns]
    df = df.rename(columns=rename_cols)
    return df

# WRITE TO CSV
# csv_file = 'data/csv/INCAL_DAILY_T2M_2015_styria_grouped.csv'
def write_to_csv(df, path):
    df.to_csv(path)

def mask_by_coords(df,lat_bounds,lon_bounds):
    lat_mask = (df['lat'] >= lat_bounds[0]) & (df['lat']<=lat_bounds[1])
    lon_mask = (df['lon'] >= lon_bounds[0]) & (df['lon']<=lon_bounds[1])
    coord_mask = lat_mask & lon_mask

    return coord_mask


def nearest_x(df,x,column):
    nearest_lat  = x
    arr          = np.array(df[column])
    diff_arr     = np.absolute(arr-nearest_lat)
    index        = np.argmin(diff_arr)
    coord        = arr[index]
    return coord



# path = "data/zamg_netcdf/t2m/2015/INCAL_HOURLY_T2M"

# netcdf_from_file = "tg_ens_mean_0.1deg_reg_2011-2021_v25.0e"
netcdf_from_file = "qq_ens_mean_0.1deg_reg_2011-2021_v25.0e"
# netcdf_from_file = "solar_styria_2011-2021"
years = '2011_2021/test'
# path = f"data/copernicus_netcdf/{years}/{netcdf_from_file}.nc"
path = f"data/copernicus_netcdf/{years}/"
# path = "data/net_cdf/t2m/2015/INCAL_DAILY_STYRIA_T2M_2015.nc"
# data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# BOX BOUNDARIES
lon_bnds, lat_bnds = (13, 16.7), (46, 48)
partial_func = partial(_preprocess, lon_bnds=lon_bnds, lat_bnds=lat_bnds)

# OPEN ALL DATASETS AT ONCE
data = xr.open_mfdataset(
    f"{path}*.nc", combine='nested', concat_dim='time', preprocess=partial_func
    # path, combine='nested', concat_dim='time', preprocess=partial_func
)

# print(data)
# OPEN ONE DATASET 
# data = xr.open_dataset(path)
# data = data.where((data['time.year']<2013),drop=True)
# print(data["time.year"])


# data = data.rename_vars({'lon':'longitude', 'lat':'latitude'})
# data = data.drop_indexes('ensemble')
# data=data.reset_index('ensemble',drop=True)
print(data)

# WRITE NETCDF FILE
# netcdf_to_file = "solar_styria_2011-2021"
# path = f"data/copernicus_netcdf/{years}/{netcdf_to_file}.nc"
# data.to_netcdf(path)

# GET AS DF
# df = convert_copernicus_to_df(data)
# df['lat'] = np.around(df['lat'],decimals=2)
# df['lon'] = np.around(df['lon'],decimals=2)

# DF TO CSV
# csv_path = f'data/csv/tair_styria_2011-2021.csv'
# df.to_csv(csv_path)
# print(df)





