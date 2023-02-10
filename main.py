import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io
import matplotlib.pyplot as plt

import transform_csv as tr
import get_data as gd
import plot_data as pl
from clipick import clipick_forPython3 as cl


def get_by_coordinates(coordinates, req_sparta, req_inca):
    df_sparta = gd.get_data(req_sparta)
    df_inca = gd.get_data(req_inca)

    frames = [df_sparta, df_inca]
    empty = False
    for f in frames:
        if gd.df_empty(f):
            empty = True
            break

    if not empty:
        # df_sparta.fillna(np.nan, inplace=True)
        # file_sparta = "data/from_sparta_test.csv"
        # tr.write_df_to_csv(df_sparta,file_sparta, False)


        print(df_sparta)
        # to_file = (f'data/to_sparta_test.csv')
        # df_sparta.to_csv(to_file, index=False)

    else:
        print("Error: Could not merge dataframes.")

def main():
    # start_date_inca = str(date.today()-timedelta(days=20))
    # end_date_inca = str(date.today()-timedelta(days=2))

    start_date_inca = "2011-03-15"
    end_time_inca = "T23:00"
    id_inca = "inca-v1-1h-1km?"
    parameters_inca = ["GL", "RH2M", "T2M", "RR"]

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
    coordinates_bad = [        
        [
            "52.032695",
            "14.966223",
        ]
    ]

    coord = [
        [
            "46.993145",
            "15.626546",
        ]
    ]
    coords_file = "coordinates/coordsList.csv"
    coords_list = get_zamg_coords_from_csv(coords_file)

    start_date_sparta = "1970-01-01"

    for c in coords_list:
        print(f"Getting data for lat {c[0]}, lon {c[1]}...")

        df_sparta  = get_spartacus(start_date_sparta,coordinates=c)
        df_inca    = get_inca(start_date_inca,id_inca,parameters_inca,end_time_inca,coordinates=c)

        coords_clipick = c.astype(float)
        lat = coords_clipick[0]
        lon = coords_clipick[1]
        df_clipick = get_clipick(Latitude=lat, Longitude=lon)

        column_names = ['TAir', 'Precip', 'RH', 'VPD']
        titles = ['Temperatures', 'Precipitation', 'Relative Humidity', 'Water Vapour Deficit']
        kinds = ['line', 'line', 'line', 'line']
        input_coords = ["48.032695", "14.966223"]
    
        plot_folder = f'plot_{c[0]}_{c[1]}'
        plot_path = pl.create_plot_folder(plot_folder)
        extension = 'png'

        for i in range(len(column_names)):
            print(f"Plotting {column_names[i]}...")
            df_inca_plottable = tr.transform_df_to_plottable(df_inca, 'Inca', column_names[i])
            df_clipick_plottable = tr.transform_df_to_plottable(df_clipick, 'Clipick', column_names[i])

            merged = tr.merge_dfs(df_clipick_plottable, df_inca_plottable)

            file = f'{plot_path}/{column_names[i]}.{extension}'
            corr_file = f'{plot_path}/{column_names[i]}_corr.csv'
            
            if i > 1:
                pl.plot_column(merged, column_names[i], titles[i], kind=kinds[i])
                pl.save_plot_to_file(file)
                # pl.show_plot()
                corr_df = merged.corr(numeric_only=True)
                corr_df.to_csv(corr_file)
                # print(f"corr: {merged.corr()}")
            else:
                df_sparta_plottable = tr.transform_df_to_plottable(df_sparta, 'Spartacus', column_names[i])
                df = tr.merge_dfs(merged, df_sparta_plottable)
                pl.plot_column(df, column_names[i], titles[i], kind=kinds[i])
                pl.save_plot_to_file(file)
                # pl.show_plot()
                # print(f"corr: {df.corr()}")
                corr_df = df.corr(numeric_only=True)
                corr_df.to_csv(corr_file)

        print(f"Plots for lat {c[0]}, lon {c[1]} done.")
        

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

if __name__ == '__main__':
    main()
