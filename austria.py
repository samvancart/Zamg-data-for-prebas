import requests
import xarray as xr
import pandas as pd
import numpy as np

# r = requests.get("https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-14T00%3A00%3A00.000Z&lat_lon=48.2%2C+15.6&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221214")
# print(r.status_code)
# https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-19T00%3A00%3A00.000Z&lat_lon=48.172858%2C+14.034002&lat_lon=47.918206%2C+14.942918&lat_lon=48.353981%2C+15.494482&lat_lon=47.693699%2C+14.220446&lat_lon=47.772126%2C+13.699956&lat_lon=47.871297%2C+15.774148&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221219
# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-14T00%3A00%3A00.000Z&lat_lon=48.2%2C+15.6&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221214"


data = xr.open_dataset("data/spartacus-daily/SPARTACUS - Spatial Reanalysis Dataset for Climate in Austria Datensatz_19610101_19611231.nc")
# print(data['Tn'])
df = data[['RR','Tx','Tn']].to_dataframe()
