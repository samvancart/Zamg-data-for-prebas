import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta

# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/inca-v1-1h-1km?parameters=GL&parameters=RH2M&parameters=RR&parameters=T2M&start=2011-03-15T00%3A00%3A00.000Z&end=2022-12-19T23%3A00%3A00.000Z&lat_lon=48.032695%2C+14.966223&lat_lon=48.03285%2C+14.963108&lat_lon=48.03678%2C+14.969155&output_format=csv&filename=INCA+analysis+-+large+domain+Datensatz_20110315T0000_20221219T2300"
# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-19T00%3A00%3A00.000Z&lat_lon=48.172858%2C+14.034002&lat_lon=47.918206%2C+14.942918&lat_lon=48.353981%2C+15.494482&lat_lon=47.693699%2C+14.220446&lat_lon=47.772126%2C+13.699956&lat_lon=47.871297%2C+15.774148&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221219"
# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-19T00%3A00%3A00.000Z&lat_lon=48.032695%2C+14.966223&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221219"


# def get_zamg(dataset, parameters, start, end, coordinates):




def build_api_call(base_url, dataset, parameters, start, end, coordinates):
    """ Builds call to zamg api

        Parameters: 
            base_url (string): url of api 
            dataset (string): Name of dataset
            parameters (list string): The values to include
            start (string): start date and time
            end (string): end date and time
            coordinates (list list string): list of coordinates as [['lat','lon'],['lat','lon']]
        Returns:
            built call (string): Call to the api with requested parameters 
    
    """
    url = base_url + dataset
    params ="parameters=" + ",".join(parameters)
    coords = list(map(",".join,coordinates))
    lat_lon = list(map(lambda old_string: "lat_lon=" + old_string, coords))
    lat_lons = "&".join(lat_lon)
    format = "output_format=csv"
    start = "start=" + start
    end = "end=" + end
    api_call_list = [url, params, start, end, lat_lons, format]
    api_call = "&".join(api_call_list)
    return api_call


url = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/"
dataset = "spartacus-v1-1d-1km?"
spartacus_params = ["RR", "Tn", "Tx"]
start_date = "1961-01-01"
start_time = "T00:00"
start = start_date + start_time
end_date = date.today()-timedelta(days=2)
end_time = "T00:00"
end = str(end_date) + end_time
coordinates = [
    [
    "48.032695",
    "14.966223",
    ],
    [
    "48.56151",
    "13.13215",
    ]
]

print(build_api_call(url,dataset, spartacus_params, start, end, coordinates))
