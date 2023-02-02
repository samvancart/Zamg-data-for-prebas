import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io

import transform_csv as tr
import get_data as gd
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
        # df_inca.fillna(np.nan, inplace=True)
        # df_sparta.fillna(np.nan, inplace=True)
        # file_inca = "data/from_inca_test.csv"
        # tr.write_df_to_csv(df_inca,file_inca, False)
        # file_sparta = "data/from_sparta_test.csv"
        # tr.write_df_to_csv(df_sparta,file_sparta, False)

        # sums = tr.calculate_daily_sums_from_hourly(df_inca)
        # file_inca = "data/to_inca_sums.csv"
        # tr.write_df_to_csv(sums,file_inca)

        df_inca = tr.transform_inca_hourly(df_inca)
       
        # df_inca.fillna("NaN", inplace=True)

        df = pd.merge_ordered(df_sparta, df_inca, on="time").fillna("NaN")
        # df = pd.merge_ordered(df_sparta, df_inca, on="time")

        print(df)

        # to_file = (f'data/combined_test_{coordinates[0]}_{coordinates[1]}.csv')
        to_file = (f'data/combined_means_and_sums.csv')
        df.to_csv(to_file, index=False)

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

    cl.getWeatherData(Latitude=48.032695, Longitude=14.966223, StartYear=1970, EndMonth=12, EndYear=2022)

    from_file = "clipick/outputs/ClipickExportedData_48.032695_14.966223.csv"
    df_clipick = pd.read_csv(from_file)
    df_clipick = tr.clipick_index_to_datetime(df_clipick)
    df_clipick = tr.transform_clipick(df_clipick)
    print(df_clipick)
    to_file = ("clipick/outputs/to_clipick.csv")
    df_clipick.to_csv(to_file, index=False)




    # for c in coord:
    #     req_sparta = gd.build_api_call(coordinates=[c])
    #     req_inca = gd.build_api_call(start_date=start_date_inca,
    #         id=id_inca, parameters=parameters_inca, end_time=end_time_inca, coordinates=[c])

    #     get_by_coordinates(c,req_sparta=req_sparta,req_inca=req_inca)




if __name__ == '__main__':
    main()
