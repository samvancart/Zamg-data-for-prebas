import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io

# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/inca-v1-1h-1km?parameters=GL&parameters=RH2M&parameters=RR&parameters=T2M&start=2011-03-15T00%3A00%3A00.000Z&end=2022-12-19T23%3A00%3A00.000Z&lat_lon=48.032695%2C+14.966223&lat_lon=48.03285%2C+14.963108&lat_lon=48.03678%2C+14.969155&output_format=csv&filename=INCA+analysis+-+large+domain+Datensatz_20110315T0000_20221219T2300"
# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-19T00%3A00%3A00.000Z&lat_lon=48.172858%2C+14.034002&lat_lon=47.918206%2C+14.942918&lat_lon=48.353981%2C+15.494482&lat_lon=47.693699%2C+14.220446&lat_lon=47.772126%2C+13.699956&lat_lon=47.871297%2C+15.774148&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221219"
# "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/spartacus-v1-1d-1km?parameters=RR&parameters=Tn&parameters=Tx&start=1961-01-01T00%3A00%3A00.000Z&end=2022-12-19T00%3A00%3A00.000Z&lat_lon=48.032695%2C+14.966223&output_format=csv&filename=SPARTACUS+-+Spatial+Reanalysis+Dataset+for+Climate+in+Austria+Datensatz_19610101_20221219"


def_url = "https://dataset.api.hub.zamg.ac.at"
def_version = "v1"
def_type = "timeseries"
def_mode = "historical"
def_id = "spartacus-v1-1d-1km?"
def_parameters = ["RR", "Tn", "Tx"]
def_start_date = "1961-01-01"
def_start_time = "T00:00"
def_end_date = "2022-12-31"
def_end_time = "T00:00"
def_coordinates = [["48.032695", "14.966223"]]
def_format = "csv"


# def get_zamg(dataset, parameters, start, end, coordinates):


def req_data(url):
    """ Requests data from zamg api

    Parameters:
        url (string): request url

        Returns:
            response (Requests.models.response object): response from zamg api

    """
    try:
        r = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return r


def build_api_call(
    base_url = def_url,
    version = def_version,
    type = def_type,
    mode = def_mode,
    id = def_id, 
    parameters=def_parameters, 
    start_date=def_start_date, 
    start_time=def_start_time,
    end_date=def_end_date,
    end_time=def_end_time, 
    coordinates=def_coordinates,
    format=def_format
    ):
    """ Builds call to zamg api

        Parameters: 
            base_url (string): url of zamg api
            version (string): api version
            type (string): type of data (station, grid, timeseries)
            mode (string): mode of data (historical, current, forecast)
            id (string): Name of dataset
            parameters (list string): The values to include in the query
            start_date (string): start date
            start_time (string): start time
            end_date (string): end date
            end_time (string): end time
            coordinates (list list string): list of coordinates as [['lat','lon'],['lat','lon']]
            format (string): format of returned data (csv, geojson, netcdf)
        Returns:
            tuple: url containing requested parameters and the id (name of dataset) 
    
    """
    
    url = "/".join([base_url, version, type, mode, id])
    params ="parameters=" + ",".join(parameters)
    coords = list(map(",".join,coordinates))
    lat_lon = list(map(lambda old_string: "lat_lon=" + old_string, coords))
    lat_lons = "&".join(lat_lon)
    format_type = "output_format=" + format
    start = "start=" + start_date + start_time
    end = "end=" + end_date + end_time
    api_call_list = [url, params, start, end, lat_lons, format_type]
    api_call = "&".join(api_call_list)
    return (api_call, id)


url = "https://dataset.api.hub.zamg.ac.at/v1/timeseries/historical/"
dataset = "spartacus-v1-1d-1km?"
spartacus_params = ["RR", "Tn", "Tx"]
start_date = "1961-01-01"
start_date= str(date.today()-timedelta(days=20))
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

def response_to_dataframe(res_content):
    df = pd.read_csv(io.StringIO(res_content.decode('utf-8')), parse_dates=['time'])
    return df

def get_data(req_tuple):
    """ Gets content from response object and creates dataframe

        Parameters:
            req_tuple (tuple): A tuple containing the url for the request and the id of the request.

        Returns:
            Dataframe (Pandas DataFrame): Response content as dataframe. Empty dataframe if no content in response. 
    
    """

    print(f'Fetching data from {req_tuple[1]}...')
    res = req_data(req_tuple[0])
    if res.status_code == 200:
        content = res.content
        df = response_to_dataframe(content)
        print("Fetched data succesfully.")
        return df
    else:
        print(f'An error occured with status code {res.status_code}.')
        print(res.content)
        return pd.DataFrame()

def df_empty(df):
    if not df.empty:
        print(df)
        return False
    else:
        print("Couldn't process empty dataframe.")
        return True

# req_url = build_api_call(coordinates=coordinates, start_date=start_date)
# data = get_data(req_url)
# print(data)
