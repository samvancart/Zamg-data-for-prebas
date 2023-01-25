import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io

import transform_csv as tr
import get_data as gd


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
        df_inca = tr.calculate_daily_averages_from_hourly(df_inca)

        df = pd.merge_ordered(df_sparta, df_inca, on="time").fillna("NaN")

        print(df)

        to_file = (f'data/combined_test_{coordinates[0]}_{coordinates[1]}.csv')
        df.to_csv(to_file, index=False)

    else:
        print("Error: Could not merge dataframes.")

def main():
    start_date_inca = str(date.today()-timedelta(days=20))
    end_date_inca = str(date.today()-timedelta(days=2))

    # start_date_inca = "2011-03-15"
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
            "48.032695",
            "14.966223",
        ]
    ]

    # req_inca = gd.build_api_call(start_date=start_date_inca, end_date=end_date_inca,
    #     id=id_inca, parameters=parameters_inca, end_time=end_time_inca)

    from_file = "data/from_inca_test.csv"
    to_file = "data/to_inca_test.csv"
    
    # df_inca = gd.get_data(req_inca)
    # df_inca.to_csv(to_file, index=False)

    df_inca = pd.read_csv(from_file, parse_dates=['time'])

    # df_inca_means = tr.calculate_daily_averages_from_hourly(df_inca)
    # df_inca_sums = tr.calculate_daily_sums_from_hourly(df_inca)

    # df_inca_means.to_csv("data/to_inca_means.csv")
    # df_inca_sums.to_csv("data/to_inca_sums.csv")    

    # print("means",df_inca_means[['RR [kg m-2]']])
    # print("sums", df_inca_sums[['RR [kg m-2]']])

    # df_inca_means[['RR [kg m-2]']] = df_inca_sums[['RR [kg m-2]']]

    # df_inca = df_inca_means

    # print(df_inca)
    df_inca = tr.daily_means_and_sums_from_hourly(df_inca)
    df_inca = tr.add_vpd(df_inca)
    print(df_inca)

    # print(df_inca.columns)
    print(tr.vpd(9.009583333333333,82.17666666666666))
    df_inca.to_csv("data/to_inca.csv")   


    

    # frames = [df_inca]
    # empty = False
    # for f in frames:
    #     if gd.df_empty(f):
    #         empty = True
    #         break

    # if not empty:
    #     df_inca = tr.calculate_daily_averages_from_hourly(df_inca)

    #     file = "data/to_inca_test.csv"
    #     df_inca = pd.read_csv(file, parse_dates=['time'])

    # else:
    #     print("Error: Could not merge dataframes.")



    

    # for c in coordinates:
    #     req_sparta = gd.build_api_call(coord=[c])
    #     req_inca = gd.build_api_call(start_date=start_date_inca,
    #         id=id_inca, parameters=parameters_inca, end_time=end_time_inca, coord=[c])

    #     get_by_coordinates(c,req_sparta=req_sparta,req_inca=req_inca)




if __name__ == '__main__':
    main()
