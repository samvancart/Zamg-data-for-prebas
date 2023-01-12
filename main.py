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
    start_date= str(date.today()-timedelta(days=20))
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
    req_url = gd.build_api_call(coordinates=coordinates, start_date=start_date)
    df = gd.get_data(req_url)
    prebas_df = tr.transform_spartacus_daily(df)
    prebas_df.to_csv("data/test.csv")


if __name__ == '__main__':
    main()