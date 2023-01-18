import requests
import xarray as xr
import pandas as pd
import numpy as np
from datetime import date
from datetime import timedelta
import io

import transform_csv as tr
import get_data as gd


def main():
    start_date = str(date.today()-timedelta(days=20))
    # start_date = "2022-12-32"
    end_date = str(date.today()-timedelta(days=2))
    end_time_inca = "T23:00"
    id_inca = "inca-v1-1h-1km?"
    parameters_inca = ["RH2M", "T2M"]

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
    # req_url_inca = gd.build_api_call(coordinates=coordinates, start_date=start_date, end_date=end_date,
    #     id=id_inca, parameters=parameters_inca, end_time=end_time_inca)
    # req_url_sparta = gd.build_api_call(coordinates=coordinates, start_date=start_date, end_date=end_date)

    # df = gd.get_data(req_url_inca)
    # if not df.empty:
    #     df.dropna(inplace=True)
    #     print(df)
    #     df.to_csv("data/from_inca_test.csv", index=False)
    # else:
    #     print("Couldn't process empty dataframe.")

    file = "data/from_inca_test.csv"
    df = pd.read_csv(file, parse_dates=['time'])
    # df = df.resample('d', on='time').mean().dropna(how='all')
    # df = df.set_index('time').groupby(pd.Grouper(freq='d')).mean().dropna(how='all')
    df2=df.groupby(df["time"].dt.hour)["RH2M [percent]"].mean()
    print(df2)
    df.to_csv("data/to_inca_test.csv")

   
    

if __name__ == '__main__':
    main()
