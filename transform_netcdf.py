import xarray as xr
import pandas as pd
import numpy as np
from netCDF4 import Dataset

path = "data/net_cdf/t2m/2015/INCAL_HOURLY_T2M_201501.nc"
data = xr.open_dataset(path)
# data = Dataset(path, 'r')

# print(data)
data=data.resample(time="1d").mean()
print(data)

lat = data.variables['lat']
lon = data.variables['lon']
time = data.variables['time']

t2m = data.variables['T2M'] 

# print(lat[250])
# print(np.shape(t2m.values[0][0]))
# print(np.shape(time))
# print(data.coords)
test_lat=lat.values
test_lon=lon.values
test_t2m=t2m.values
test_time = time.values
# print(time)
# print(np.shape(test_t2m))
# print(test_time)






# print(np.shape(test_t2m))
# d = {'time':test_time, 'T2M':test_t2m, 'lat':lat, 'lon':lon}
# d = {'T2M':test_t2m}
# df = pd.DataFrame(data=d)
df = data.to_dataframe()
# lat_bounds=df.loc[(df['lat'] >= 46) & (df['lat'] <= 47.4)]
# lon_bounds=df.loc[(df['lon'] >= 13) & (df['lon'] <= 16.7)]
df=df.loc[(df['lat'] >= 46) & (df['lat'] <= 47.4) & (df['lon'] >= 13) & (df['lon'] <= 16.7)]
df=df[['T2M','lat','lon']]
new_index=df.index.droplevel(['x', 'y'])
df.set_index(new_index, inplace=True)
# print(df.index)
# print(df.columns)
# df = pd.merge(lat_bounds,lon_bounds)
file = 'data/INCAL_DAILY_T2M_201501.styria.csv'
df.to_csv(file)
print(df)







