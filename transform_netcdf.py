import xarray as xr
import pandas as pd
import numpy as np
from functools import partial
from math import radians, cos, sin, asin, sqrt
import os
import transform_csv as tr



def _preprocess(x, lon_bnds, lat_bnds):
    # Configure variable names
    # coords = list(x.coords)
    # ds = x
    # if 'lon' in coords or 'lat' in coords:
    #     ds = ds.rename_vars({'lon':'longitude', 'lat':'latitude'})

    # Remove unwanted data by coordinates
    # ds = x.where((x.latitude<=lat_bnds[1]) & (x.latitude>=lat_bnds[0]) & (x.longitude<=lon_bnds[1]) & (x.longitude>=lon_bnds[0]), drop=True)
    ds = x.where((x.lat<=lat_bnds[1]) & (x.lat>=lat_bnds[0]) & (x.lon<=lon_bnds[1]) & (x.lon>=lon_bnds[0]), drop=True)

    # Remove unwanted years
    data = ds.where((ds['time.year']>=1992),drop=True)
    # Return daily means
    # return ds.resample(time="1d").mean()
    return data


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
def convert_copernicus_to_df(dataset, vars):
    df = dataset.to_dataframe()
    df.reset_index(inplace=True)
    df.set_index(df['time'], inplace=True)
    df=df[vars]
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

def get_files_in_folder(path):
    files = []
    for filename in os.listdir(path):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)
            files.append(f)
    return files

# path = "data/zamg_netcdf/t2m/2015/INCAL_HOURLY_T2M"

# netcdf_from_file = "tg_ens_mean_0.1deg_reg_2011-2021_v25.0e"
netcdf_from_file = "rr_ens_mean_0.1deg_reg_1980-1994_v25.0e"
# netcdf_from_file = "solar_styria_2011-2021"
years = '2011_2021/test'
folder = 'other_vars'
path = f"data/copernicus_netcdf/{folder}/{netcdf_from_file}.nc"
path = f"data/copernicus_netcdf/{folder}/"
# path = "data/net_cdf/t2m/2015/INCAL_DAILY_STYRIA_T2M_2015.nc"
# data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# BOX BOUNDARIES
lon_bnds, lat_bnds = (13, 16.7), (46, 48)
partial_func = partial(_preprocess, lon_bnds=lon_bnds, lat_bnds=lat_bnds)

# OPEN ALL DATASETS AT ONCE
# data = xr.open_mfdataset(
#     # f"{path}*.nc", combine='nested', concat_dim='time', preprocess=partial_func
#     # path, combine='nested', concat_dim='time', preprocess=partial_func
#     f"{path}*.nc", combine='nested', concat_dim='time'
# )

# print(data)
# OPEN ONE DATASET 
# data = xr.open_dataset(path)
# data = data.where((data['time.year']<2013),drop=True)
# print(data["time.year"])


# MANUALLY OPEN MANY DATASETS
# files = get_files_in_folder(path)
# df_all = pd.DataFrame()
# for index, file in enumerate(files):
#     data = xr.open_dataset(file)
#     data = _preprocess(data,lon_bnds,lat_bnds)
#     vars = ['qq', 'lat', 'lon']
#     df = convert_copernicus_to_df(data, vars)
#     df['lat'] = np.around(df['lat'],decimals=2)
#     df['lon'] = np.around(df['lon'],decimals=2)
#     print(df)
#     if index == 0:
#         df_all = df
#     else:
#         df_all = pd.concat([df_all, df], axis=0)
# print(df_all)


# data = data.rename_vars({'lon':'longitude', 'lat':'latitude'})
# data = data.drop_indexes('ensemble')
# data=data.reset_index('ensemble',drop=True)

# data = _preprocess(data,lon_bnds,lat_bnds)
# print(data.head(5))

# WRITE NETCDF FILE
# netcdf_to_file = "tg_styria_1994"
# path = f"data/copernicus_netcdf/{folder}/{netcdf_to_file}.nc"
# data.to_netcdf(path)

# GET AS DF
# vars = ['rr', 'latitude', 'longitude']
# df = convert_copernicus_to_df(data.head(5), vars)
# df['lat'] = np.around(df['lat'],decimals=2)
# df['lon'] = np.around(df['lon'],decimals=2)
# print(df)

# DF TO CSV
# csv_path = f'data/csv/qq_styria_1992-2021.csv'
# df_all.to_csv(csv_path)
# print(df_all)

## MERGE DATASETS
# path = "data/csv/"
# tg = path+"tg_styria_1992-2021.csv"
# rr = path+"rr_styria_1992-2021.csv"
# hu = path+"hu_styria_1992-2021.csv"
# qq = path+"qq_styria_1992-2021.csv"

# df_tg = pd.read_csv(tg, parse_dates=['time'])
# df_rr = pd.read_csv(rr, parse_dates=['time'])
# df_hu = pd.read_csv(hu, parse_dates=['time'])
# df_qq = pd.read_csv(qq, parse_dates=['time'])



# df1 = pd.merge(df_tg,df_rr)
# df2 = pd.merge(df_hu,df_qq)
# df = pd.merge(df1,df2)
# print(df)

# csv_path = f'data/csv/all_styria_1992-2021.csv'
# df.to_csv(csv_path)

# TO PREBAS
csv_path = f'data/csv/all_styria_1992-2021.csv'
df = pd.read_csv(csv_path, parse_dates=['time'])

df.drop(df.columns[[0]], axis=1, inplace=True)


df['DOY'] = df['time'].dt.day_of_year
grouped = df.groupby(["lat", "lon"],as_index=True)
df['climID'] = grouped.grouper.group_info[0]


df = tr.add_value(df, 'rss', tr.convert_gl_to_rss)
df = tr.add_value(df, 'PAR', tr.calculate_par)
df = tr.add_value(df, 'VPD', tr.calculate_vpd_copernicus)


cols = {'tg':'TAir','rr': 'Precip'}
df = df.rename(columns=cols)

df = df[['time','DOY','climID','PAR', 'TAir', 'VPD', 'Precip', 'lat', 'lon']]

print(df.head(5))

csv_path = f'data/csv/prebas_1992-2021.csv'
df.to_csv(csv_path, index=False)



