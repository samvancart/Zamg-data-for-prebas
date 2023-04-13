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
    # ds = x.where((x.lat<=lat_bnds[1]) & (x.lat>=lat_bnds[0]) & (x.lon<=lon_bnds[1]) & (x.lon>=lon_bnds[0]), drop=True)

    # Remove unwanted years
    # data = ds.where((ds['time.year']>=1992),drop=True)
    y = x['RR']
    # Return daily sums
    sums = y.resample(time="1d").sum()
    # Return daily means
    means = x[['T2M', 'GL', 'RH2M']]
    means = means.resample(time="1d").mean()

    return xr.merge([means,sums])
    # return data


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
    row = df.loc[distances.idxmin()]
    return row['climID']



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

for i, y in enumerate(range(2016,2022)):
    print(f'Processing {y}')

# path = "data/zamg_netcdf/t2m/2015/INCAL_HOURLY_T2M"

# netcdf_from_file = "tg_ens_mean_0.1deg_reg_2011-2021_v25.0e"
    netcdf_from_file = str(y)
    # netcdf_from_file = "solar_styria_2011-2021"
    # years = '2011_2021/test'
    folder = 'processed'
    path = f"data/zamg_netcdf/{folder}/{netcdf_from_file}.nc"
# path = f"data/zamg_netcdf/{folder}/"
# path = f"data/zamg_netcdf/all/2015-01-01.nc"
# path = "data/net_cdf/t2m/2015/INCAL_DAILY_STYRIA_T2M_2015.nc"
# data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# BOX BOUNDARIES
# lon_bnds, lat_bnds = (13, 16.7), (46, 48)
# partial_func = partial(_preprocess, lon_bnds=lon_bnds, lat_bnds=lat_bnds)

# OPEN ALL DATASETS AT ONCE
# data = xr.open_mfdataset(
#     # f"{path}*.nc", combine='nested', concat_dim='time', preprocess=partial_func
#     # path, combine='nested', concat_dim='time', preprocess=partial_func
#     f"{path}*.nc", combine='nested', concat_dim='time'
# )

# print(data)

# OPEN ONE DATASET 
    data = xr.open_dataset(path)
    # data = _preprocess(data,lon_bnds,lat_bnds)
    # data = data.where((data.y == 449000) & (data.x == 655000), drop=True)
    data = data.reset_index(['x','y'],drop=True)
    # print(data)
    df = data.to_dataframe()
    df = df.droplevel(['x','y'])
    # print(df)
    grouped = df.groupby(["lat", "lon"],as_index=True)
    df['climID'] = grouped.grouper.group_info[0]
    # df['time'] = df.index
    df.reset_index(level=[0],inplace=True)

# print(df)
# df.to_csv('data/csv/inca_processed_test.csv')
# data = data.where((data['time.year']<2013),drop=True)
# print(data["time.year"])

# df = pd.read_csv('data/csv/inca_one_day_ids.csv', parse_dates=['time'])
# sites = pd.read_csv('data/csv/esa_sites.csv')
# df = df.head(500)
# print(df)

# print(sites)

# SLICE DF TO SITES FILE MIN AND MAX LAT LON
# lat_bnds = (sites['lat'].min(), sites['lat'].max())
# lon_bnds = (sites['lon'].min(), sites['lon'].max())
# df_bnds = df[(df['lat']<=lat_bnds[1]) & (df['lat']>=lat_bnds[0]) & (df['lon']<=lon_bnds[1]) & (df['lon']>=lon_bnds[0])]
# # print(df_bnds)

# APPLY NEAREST NEIGHBOUR TO SITES
# sites['climID'] = sites.apply(lambda x: find_nearest_coords(df_bnds, x['lat'], x['lon']), axis=1)
# sites.to_csv('data/csv/inca_sites_ids.csv')





# TEST NEAREST NEIGHBOUR ALGORITHM
# site_lat1=47.05927285
# site_lon1=14.47159723
# nearest1 = find_nearest_coords(df, site_lat1, site_lon1)
# site_lat5=47.05561656
# site_lon5=14.69151105
# nearest5 = find_nearest_coords(df, site_lat5, site_lon5)
# site_lat171=46.90412902
# site_lon171=15.04051856
# nearest171 = find_nearest_coords(df, site_lat171, site_lon171)
# site_lat1346=47.10388339
# site_lon1346=14.98267642
# nearest1346 = find_nearest_coords(df, site_lat1346, site_lon1346)
# print(nearest1)
# print(nearest5)
# print(nearest171)
# print(nearest1346)


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
# netcdf_to_file = str(year)
# path = f"data/zamg_netcdf/processed/{netcdf_to_file}.nc"
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
# csv_path = f'data/csv/inca_processed_test.csv'
# df = pd.read_csv(csv_path, parse_dates=['time'])


    df['DOY'] = df['time'].dt.day_of_year

    def calculate_vpd_from_np_arrays(tair,rh):
        svp = 610.7 * 10**(7.5*tair/(237.3+tair))
        vpd = svp * (1-(rh/100)) / 1000
        return vpd

    gl = np.array(df['GL'])
    applyrss = np.vectorize(lambda x: x*0.0864)
    rss = applyrss(gl)

    applypar = np.vectorize(lambda x: x *0.44*4.56)
    par = applypar(rss)

    tair = np.array(df['T2M'])
    rh = np.array(df['RH2M'])
    applyvpd = np.vectorize(calculate_vpd_from_np_arrays)
    vpd = applyvpd(tair,rh)


    cols = {'T2M':'TAir','RR': 'Precip'}
    df = df.rename(columns=cols)
    df['PAR'] = par
    df['VPD'] = vpd

    df = df[['time','DOY','climID','PAR', 'TAir', 'VPD', 'Precip', 'lat', 'lon']]

    print(df)

    year = str(y)
    csv_path = f'data/csv/inca/prebas_inca_styria_{year}.csv'
    df.to_csv(csv_path, index=False)
    print(f'{y}.csv done.')



