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

    # req_inca = gd.build_api_call(start_date=start_date_inca, end_date=end_date_inca,
    #     id=id_inca, parameters=parameters_inca, end_time=end_time_inca)

    # from_file = "data/from_inca_test.csv"
    # df_inca = pd.read_csv(from_file, parse_dates=['time']).fillna(np.nan)
    # from_file = "data/from_sparta_test.csv"
    # df_sparta = pd.read_csv(from_file, parse_dates=['time']).fillna(np.nan)

    # df_inca = tr.transform_inca_hourly(df_inca)

    # df = pd.merge_ordered(df_sparta, df_inca, on="time").fillna("NaN")
    # to_file = (f'data/combined_means_and_sums.csv')
    # print(df)
    # df.to_csv(to_file, index=False)

    start_date_sparta = "1970-01-01"

    # req_inca = gd.build_api_call(start_date=start_date_inca, 
    #     id=id_inca, parameters=parameters_inca, end_time=end_time_inca)
    # df_inca = gd.get_data(req_inca)

    # df_inca.fillna(np.nan, inplace=True)
    # file_inca = "data/from_inca_test.csv"
    # tr.write_df_to_csv(df_inca, file_inca, False)

    # print(df_inca.isnull().values.any())
    # df_inca = tr.transform_inca_hourly(df_inca)
    # print(df_inca)

    # to_file = (f'data/to_inca_test.csv')
    # df_inca.to_csv(to_file)

    from_file = (f'data/to_inca_test.csv')
    df_inca = pd.read_csv(from_file, parse_dates=['time'])
    


    # GET AND TRANSFORM SPARTACUS
    # req_sparta = gd.build_api_call(start_date=start_date_sparta)
    # df_sparta = gd.get_data(req_sparta)

    # df_sparta.fillna(np.nan, inplace=True)
    # file_sparta = "data/from_sparta_test.csv"
    # tr.write_df_to_csv(df_sparta,file_sparta, False)

    # print(df_sparta.isnull().values.any())
    # df_sparta = tr.transform_spartacus_daily(df_sparta)
    # print(df_sparta)

    # to_file = (f'data/to_sparta_test.csv')
    # df_sparta.to_csv(to_file)

    from_file = (f'data/to_sparta_test.csv')
    df_sparta = pd.read_csv(from_file, parse_dates=['time'])

    # clipick_lat = df_sparta[['lat']].iloc[0][0]
    # clipick_lon = df_sparta[['lon']].iloc[0][0]
    # print(clipick_lat)
    # print(clipick_lon)

    # GET AND TRANSFORM CLIPICK
    # cl.getWeatherData(Latitude=48.032695, Longitude=14.966223, StartYear=1970, EndMonth=12, EndYear=2022)

    # from_file = "clipick/outputs/ClipickExportedData_48.032695_14.966223.csv"
    # df_clipick = pd.read_csv(from_file)
    # df_clipick = tr.clipick_index_to_datetime(df_clipick)
    # df_clipick = tr.transform_clipick(df_clipick)
    # print(df_clipick)
    # to_file = ("clipick/outputs/to_clipick.csv")
    # df_clipick.to_csv(to_file)

    from_file = (f"clipick/outputs/to_clipick.csv")
    df_clipick = pd.read_csv(from_file, parse_dates=['time'])
    df_tair_sparta = df_sparta[['time','TAir']].copy()
    df_tair_sparta = df_tair_sparta.rename(columns = {'TAir':'TAir Spartacus'})
    df_tair_sparta['time'] = df_tair_sparta['time'].dt.date
    df_tair_inca = df_inca[['time','TAir']].copy()
    df_tair_inca = df_tair_inca.rename(columns = {'TAir':'TAir Inca'})
    df_tair_inca['time'] = df_tair_inca['time'].dt.date
    df_tair_clipick = df_clipick[['time','TAir']].copy()
    df_tair_clipick = df_tair_clipick.rename(columns = {'TAir':'TAir Clipick'})
    df_tair_clipick['time'] = pd.to_datetime(df_tair_clipick['time']).dt.date
    print(df_tair_clipick)
    print(df_tair_sparta)
    print(df_tair_inca)

    df1 = pd.merge_ordered(df_tair_sparta, df_tair_inca, on="time").fillna(np.nan)
    df = pd.merge_ordered(df1, df_tair_clipick, on="time").fillna(np.nan)
    print(df)
    # df_tair_sparta.set_index(df_sparta.index)
    # print(df_tair_sparta)

    # df = pd.merge_ordered(df_sparta, df_inca, df_clipick, on="time").fillna("NaN")

    column_tair = 'TAir'
    label_sparta  = "Spartacus"
    label_inca    = "Inca"
    label_clipick = "Clipick"
    # pl.plot_multile_columns(
    #     [(df_sparta, label_sparta), (df_inca, label_inca), (df_clipick, label_clipick)],'TAir', "Temperature")
    np_index = df_clipick['time'].to_numpy()
    x_values = np_index
    print(x_values)
    # y_values = np.array(
    #     [df_sparta[column_tair].to_numpy(), df_inca[column_tair].to_numpy(), df_clipick[column_tair].to_numpy()])
    np_clipick = df_clipick[column_tair].to_numpy()
    np_sparta = df_sparta[column_tair].to_numpy()
    np_inca = df_inca[column_tair].to_numpy()
    y_values = np.array([np_clipick,np_sparta])
    print(np_clipick)
    print(x_values.shape)
    print(y_values.shape)
    # plt.plot(df_sparta[column_tair], label=label_sparta, color='green')
    # plt.plot(df_inca[column_tair], label=label_inca, color='steelblue')
    # plt.plot(df_clipick[column_tair], label=label_clipick, color='purple')

    # plt.plot(x_values, y_values)

    df.plot(x='time',kind='line')

    plt.legend(title='Databases')

    plt.ylabel(column_tair, fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Temperatures', fontsize=16)

    plt.show()

    # for c in coord:
    #     req_sparta = gd.build_api_call(coordinates=[c])
    #     req_inca = gd.build_api_call(start_date=start_date_inca,
    #         id=id_inca, parameters=parameters_inca, end_time=end_time_inca, coordinates=[c])

    #     get_by_coordinates(c,req_sparta=req_sparta,req_inca=req_inca)




if __name__ == '__main__':
    main()
