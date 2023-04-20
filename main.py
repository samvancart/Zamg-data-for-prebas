import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io
import matplotlib.pyplot as plt

import transform_csv as tr
import transform_netcdf as trn
import get_data as gd
import plot_data as pl
import normalise_data as nd
from clipick import clipick_forPython3 as cl

from dateutil import rrule
from datetime import datetime



def main():
    a = '20200101'
    b = '20211231'

def get_for_coords(coordinates = [
        [
            "46.993145",
            "15.626546",
        ]
    ], 
    start_date_inca = "2011-03-15",
    end_time_inca = "T23:00",
    id_inca = "inca-v1-1h-1km?",
    parameters_inca = ["GL", "RH2M", "T2M", "RR"],
    start_date_sparta = "1970-01-01",):
    
    coords_list = np.array(coordinates)

    # Get data for each coordinate c
    for c in coords_list:
        print(f"Getting data for lat {c[0]}, lon {c[1]}...")

        # GET DATA
        df_inca    = get_inca(start_date_inca,id_inca,parameters_inca,end_time_inca,coordinates=c)
        
        coords_clipick = c.astype(float)
        lat = coords_clipick[0]
        lon = coords_clipick[1]
        df_clipick = get_clipick(Latitude=lat, Longitude=lon)

        # FILTER DF BY DATES
        df_filtered_clipick = nd.filter_df_by_date(df_clipick)

        # GET MEANS OF YEARLY SUMS
        inca_annual_pr_sum_mean = nd.get_combined_annual_mean(df_inca)
        clipick_annual_pr_sum_mean = nd.get_combined_annual_mean(df_filtered_clipick)

        # GET BIAS CORRECTED VALUES
        daily_bias = (inca_annual_pr_sum_mean-clipick_annual_pr_sum_mean)/365
        delta = nd.get_deltas(df_inca, df_filtered_clipick)
        delta['Precip'] = daily_bias
        df_clipick = nd.get_modified_df(df_clipick, delta, nd.get_bias_vals)

        # GET QUANTILE DF:S
        df_clipick_q = nd.get_quantile_df(df_clipick)
        df_inca_q    = nd.get_quantile_df(df_inca)

        # NORMALISE AND RESCALE
        df_clipick = nd.norm_and_rescale(df_clipick, df_clipick_q, df_inca_q)

        # GET INTRA CORRELATION
        inca_corr = correlation_with_all(df_inca, 'RSS', ['lat','lon'])
        clipick_corr = correlation_with_all(df_clipick, 'RSS')
        data = {'INCA':inca_corr, 'CLIPICK_NORM':clipick_corr}
        df_corr = get_corr_df(data)

        # WRITE INTRA CORRELATION TO FILE
        path = 'inca_clipick_normalised'
        plot_path = get_plot_path(path, c)
        intra_correlations_to_csv(df_corr, plot_path)

        # WRITE DELTAS TO FILE
        deltas_file = f'{plot_path}/deltas.csv'
        delta.dropna(inplace=True)
        delta.to_csv(deltas_file)

        # VARIABLES FOR PLOTTING
        column_names = ['TAir', 'Precip', 'RH', 'VPD', 'RSS']
        titles = ['Temperatures', 'Precipitation', 'Relative Humidity', 'Water Vapour Deficit', 'Solar Radiation']
        kinds = ['line', 'line', 'line', 'line', 'line']

        # CREATE PLOTS
        get_plots_for_pair(df_inca, df_clipick, 'Inca', 'Clipick_NORM', c,
                           column_names, titles, kinds, plot_path)

# Create folder path for plots
def get_plot_path(folder_name, c):
    plot_folder = f'{folder_name}_{c[0]}_{c[1]}'
    plot_path = pl.create_plot_folder(plot_folder)
    return plot_path

# Create file for correlations
def intra_correlations_to_csv(df, path):
    corr_file = f'{path}/intra_correlations.csv'
    print(f'Writing intra correlations file...')
    df.fillna('NaN', inplace=True) # If 'NaN' causes problems replace with np.nan
    df.to_csv(corr_file)
    print('Done.')

# Plot two dataframes
def get_plots_for_pair(df1, df2, df1_name, df2_name, c, column_names, titles, kinds, plot_path, extension='png'):

    # Create plots for each column
    for i in range(len(column_names)):
        print(f"Plotting {column_names[i]}...")
        df1_plottable = tr.transform_df_to_plottable(df1, df1_name, column_names[i])
        df2_plottable = tr.transform_df_to_plottable(df2, df2_name, column_names[i])

        merged = tr.merge_dfs(df2_plottable, df1_plottable)

        file = f'{plot_path}/{column_names[i]}.{extension}'
        
        pl.plot_column(merged, column_names[i], titles[i], kind=kinds[i])
        pl.save_plot_to_file(file)


    print(f"Plots for lat {c[0]}, lon {c[1]} done.")
    print(f'Plot path: {plot_path}')


def get_spartacus(start_date_sparta, coordinates=[["48.032695", "14.966223"]]):
    req_sparta = gd.build_api_call(start_date=start_date_sparta)
    df_sparta = gd.get_data(req_sparta)
    df_sparta.fillna(np.nan, inplace=True)
    df_sparta = tr.transform_spartacus_daily(df_sparta)
    df_sparta = index_to_time_col(df_sparta)
    return df_sparta

def get_inca(start_date_inca,id_inca,parameters_inca,end_time_inca, coordinates=[["48.032695", "14.966223"]]):
    req_inca = gd.build_api_call(start_date=start_date_inca, 
        id=id_inca, parameters=parameters_inca, end_time=end_time_inca)
    df_inca = gd.get_data(req_inca)
    df_inca.fillna(np.nan, inplace=True)
    df_inca = tr.transform_inca_hourly(df_inca)
    df_inca = index_to_time_col(df_inca)
    return df_inca

def get_clipick(Latitude=48.032695, Longitude=14.966223, StartYear=1970, EndMonth=12, EndYear=2022):
    df_clipick = cl.getWeatherData(Latitude=Latitude, Longitude=Longitude, StartYear=1970, EndMonth=12, EndYear=2022)
    df_clipick = tr.clipick_index_to_datetime(df_clipick)
    df_clipick = tr.transform_clipick(df_clipick)
    df_clipick = index_to_time_col(df_clipick)
    return df_clipick

# Make index a column
def index_to_time_col(df):
    df.reset_index(inplace=True)
    df = df.rename(columns = {'index':'time'})
    return df

# Read coordinates from csv and return list of coordinates as [['lat', 'lon'], ['lat', 'lon']].
def get_zamg_coords_from_csv(coords_file):
    coords_file = "coordinates/coordsList.csv"
    df_coords = pd.read_csv(coords_file)
    coords_list = np.array(df_coords).astype(str)
    return coords_list

# Intra correlations
def correlation_with_all(df, col_name, drop_cols=[]):
    for col in drop_cols:
        df.drop([col], axis=1, inplace=True)
    corr = df.corrwith(df[col_name], numeric_only=True)
    return corr

# Correlations as df
def get_corr_df(data):
    df_corr = pd.DataFrame(data=data)
    return df_corr


if __name__ == '__main__':
    main()
