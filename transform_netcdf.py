import xarray as xr
import pandas as pd
import numpy as np
from netCDF4 import Dataset
from functools import partial
from math import radians, cos, sin, asin, sqrt

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

def _preprocess(x, lon_bnds, lat_bnds):
    # Remove unwanted data by coordinates
    ds = x.where((x.latitude<=lat_bnds[1]) & (x.latitude>=lat_bnds[0]) & (x.longitude<=lon_bnds[1]) & (x.longitude>=lon_bnds[0]), drop=True)
    # Return daily means
    # return ds.resample(time="1d").mean()
    return ds

# path = "data/zamg_netcdf/t2m/2015/INCAL_HOURLY_T2M"

# netcdf_from_file = "tg_ens_mean_0.1deg_reg_2011-2021_v25.0e"
netcdf_from_file = "tair_styria_2011-2021"
path = f"data/copernicus_netcdf/{netcdf_from_file}.nc"
# path = "data/net_cdf/t2m/2015/INCAL_DAILY_STYRIA_T2M_2015.nc"
# data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# BOX BOUNDARIES
# lon_bnds, lat_bnds = (13, 16.7), (46, 47.4)
# partial_func = partial(_preprocess, lon_bnds=lon_bnds, lat_bnds=lat_bnds)

# OPEN ALL DATASETS AT ONCE
# data = xr.open_mfdataset(
#     # f"{path}_*.nc", combine='nested', concat_dim='time', preprocess=partial_func
#     path, combine='nested', concat_dim='time', preprocess=partial_func
# )

# OPEN ONE DATASET 
data = xr.open_dataset(path)
# print(data)

# WRITE NETCDF FILE
# netcdf_to_file = "tair_styria_2011-2021"
# path = f"data/copernicus_netcdf/{netcdf_to_file}.nc"
# data.to_netcdf(path)

# CONVERT TO DF
def convert_copernicus_to_df(dataset):
    df = dataset.to_dataframe()
    df.reset_index(inplace=True)
    df.set_index(df['time'], inplace=True)
    df=df[['tg','latitude','longitude']]
    df.rename(columns={'latitude':'lat', 'longitude':'lon'}, inplace=True)
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


df_cop = convert_copernicus_to_df(data)

inca_file = f'data/csv/INCAL_DAILY_T2M_2015_styria.csv'
df_inca = pd.read_csv(inca_file, parse_dates=['time'])



start_date = "2015-01-01"
end_date   = "2015-12-31"
mask = (df_cop.index >= start_date) & (df_cop.index <= end_date)
df_cop=df_cop.loc[mask]

# grouped = df_cop.groupby(["lat", "lon"], as_index=False)
# df_cop = pd.concat([g for _, g in grouped])
csv_file = 'data/csv/copernicus_styria_2015.csv'

# write_to_csv(df_cop, csv_file)

# coord_mask_cop = mask_by_coords(df_cop, (46.65,46.75),(13.05,13.15))
# coord_mask_inca = mask_by_coords(df_inca, (46.65,46.75),(13.05,13.06))
# masked_cop  = df_cop.loc[coord_mask_cop]
# masked_inca = df_inca.loc[coord_mask_inca]

df_cop['lat'] = np.around(df_cop['lat'],decimals=2)
df_cop['lon'] = np.around(df_cop['lon'],decimals=2)

# print(df_cop)

# nearest_df = find_nearest_coords(df_inca, 47.05, 15.05)
# print(nearest_df)

# nearest_lat  = 47.12
# nearest_lon  = 15.11
# lat_cop  = nearest_x(df_cop, nearest_lat, 'lat')
# lon_cop = nearest_x(df_cop, nearest_lon, 'lon')

mask_cop = (df_cop['lat']==47.05) & (df_cop['lon']==15.05)
print('masked copernicus')
print(df_cop.loc[mask_cop])
mask_inca = (df_inca['lat']==47.04577) & (df_inca['lon']==15.044007)
print('masked inca')
print(df_inca.loc[mask_inca])



# lat_inca  = nearest_x(df_inca, nearest_lat, 'lat')
# lon_inca = nearest_x(df_inca, nearest_lon, 'lon')

# print('lat inca')
# print(lat_inca)
# print('lon inca')
# print(lon_inca)

# coord_mask_cop = (df_cop['lat']==nearest_lat) & (df_cop['lon']==nearest_lon)
# coord_mask_inca = (df_inca['lat']==lat_inca) & (df_inca['lon']==lon_inca)
# masked_cop  = df_cop.loc[coord_mask_cop]
# masked_inca = df_inca.loc[coord_mask_inca]

# print('Copernicus')
# print(masked_cop)
# print('Inca')
# print(masked_inca)

# print(df_inca.loc[coord_mask])
# print(df)



# DROP NAN VALUES
# df.dropna(inplace=True)

# GROUP BY COORDINATES
# grouped = df.groupby(["lat", "lon"],as_index=False)
# df = pd.concat([g for _, g in grouped])








