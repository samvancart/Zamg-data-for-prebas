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
    # coords_list = np.array(coord)
    start_date_sparta = "1970-01-01"

    # get_for_coords(coordinates=coords_list)
    # get_for_coords()

    # df_clipick = cl.getWeatherData(Latitude=48.032695, Longitude=14.966223, StartYear=1970, EndMonth=12, EndYear=2022)
    # file = (f'data/from_clipick_test.csv')
    # df_clipick.to_csv(file, index=False)

    inca_file = f'data/to_inca.csv'
    df_inca = pd.read_csv(inca_file, parse_dates=['time'])
    clipick_file = f'data/to_clipick.csv'
    df_clipick = pd.read_csv(clipick_file, parse_dates=['time'])
    filtered_clipick = filter_df_by_date(df_clipick)

    inca_annual_pr_sum_mean = get_combined_annual_mean(df_inca)
    clipick_annual_pr_sum_mean = get_combined_annual_mean(filtered_clipick)

    daily_bias = (inca_annual_pr_sum_mean-clipick_annual_pr_sum_mean)/365
    print(daily_bias)

    deltas = get_deltas(df_inca,filtered_clipick)
    print(deltas)
    deltas['Precip'] = daily_bias
    print(deltas)

    # GET BIAS CORRECTED VALUES
    df_clipick_bs = get_modified_df(filtered_clipick, deltas, get_bias_vals)
    print(df_clipick_bs)

    # GET ALL QUANTILES
    clipick_q = df_clipick_bs.quantile([.05, .95], numeric_only=True)
    inca_q = df_inca.quantile([.05, .95], numeric_only=True)

    # GET PRECIPITATION QUANTILES FOR NONZERO ONLY
    clipick_q_precip = get_nonzero_quantiles(df_clipick_bs)
    inca_q_precip = get_nonzero_quantiles(df_inca)

    # REPLACE DF PRECIP QUANTILE
    clipick_q['Precip'] = clipick_q_precip.values
    inca_q['Precip'] = inca_q_precip.values

    # RESET INDEX
    clipick_q.reset_index(drop=True, inplace=True)
    inca_q.reset_index(drop=True, inplace=True)

    # NORMALIZE DATA
    df_clipick_norm = get_modified_df(df_clipick_bs, clipick_q, get_norm_vals)
    print("BIAS CORR")
    print(df_clipick_bs)
    print("NORMALISED")
    print(df_clipick_norm)

    # RESCALE DATA
    df_clipick_rescaled = get_modified_df(df_clipick_norm, inca_q, rescale_vals)
    print(df_clipick_rescaled)

    file = (f'data/to_clipick_norm_rescaled.csv')
    df_clipick_rescaled.to_csv(file, index=False)

    

def get_nonzero_quantiles(df,c='Precip',quantile=[.1, .9]):
    mask_new = df[c]
    new = mask_new.where(mask_new>0)
    precip_q = new.quantile(quantile)
    return precip_q

def get_modified_df(df, series, function):
    """ Replaces original dataframe values with modified ones
    Parameters:
        df (pandas dataframe): dataframe with original values
        series (pandas series): series with new constants for each column in df (names must match df column names)
    Returns:
        dataframe: dataframe with modified values
    """
    mod_d = {}
    for c in df.columns:
        if c in series:
            vals = function(c, df, series)
            mod_d.update({c:vals})
        else:
            mod_d.update({c:df[c]})
    df_mod = pd.DataFrame(data=mod_d)
    return df_mod

def rescale_vals(c,df, q):
    min = q.loc[0]
    max = q.loc[1]
    if c == 'Precip':
        vals = df[c].apply(lambda x: (x * (max[c] - min[c]) + min[c]) if x>0 else x)
        return vals
    else:
        vals = (df[c] * (max[c] - min[c]) + min[c])
        return vals

def get_norm_vals(c,df, q):
    min = q.loc[0]
    max = q.loc[1]
    if c == 'Precip':
        vals = df[c].apply(lambda x: (x-min[c])/(max[c]-min[c]) if x>0 else x)
        return vals
    else:
        vals = (df[c]-min[c])/(max[c]-min[c])
        return vals


# Mean of annual sums
def get_combined_annual_mean(df):
    df_annual_pr_sum = get_annual_sums(df)
    return df_annual_pr_sum.mean()


def get_annual_sums(df, value='Precip'):
    grouped = df.groupby(df['time'].dt.year)[value].sum()
    return grouped

def get_annual_means(df, value='Precip'):
    grouped = df.groupby(df['time'].dt.year)[value].mean()
    return grouped

def filter_df_by_date(df, start_date='2011-03-15', end_date='2022-12-31'):
    filtered = df.loc[(df['time'] >= start_date )
                      & (df['time'] <= end_date )]
    return filtered

# Returns deltas for means as series
def get_deltas(df1,df2):
    means1 = df1.mean(numeric_only=True)
    means2 = df2.mean(numeric_only=True)
    delta = means1 - means2
    return delta

def get_bias_vals(c,df,delta):
    if c == 'Precip':
        vals = df[c].apply(lambda x: x+delta[c] if x>0 else x)
        return vals
    else:
        vals = df[c]+delta[c]
        return vals
    
def get_bias_corrected_df(df, delta):
    """ Adds bias corrected values to original dataframe values
    Parameters:
        df (pandas dataframe): dataframe with original values
        delta (pandas series): series with correction biases for each column in df (names must match df column names)
    Returns:
        dataframe: dataframe of bias corrected values
    """
    biases_d = {}
    for c in df.columns:
        if c in delta:
            # vals=df[c]+delta[c]
            vals = get_bias_vals(c, df, delta)
            biases_d.update({c:vals})
        else:
            biases_d.update({c:df[c]})
    df_bias_corr = pd.DataFrame(data=biases_d)
    return df_bias_corr


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

        # GET BIAS CORRECTED VALUES
        df_filtered_clipick = filter_df_by_date(df_clipick)
        delta = get_deltas(df_inca, df_filtered_clipick)
        df_clipick = get_bias_corrected_df(df_filtered_clipick, delta)
        # df_bias_corr = get_bias_corrected_df(df_filtered_clipick, delta)
        # df_clipick = get_bias_corrected_df(df_clipick, delta)

        # CONCAT BIAS CORR DF WITH ORIGINAL
        # df_clipick_start = filter_df_by_date(df_clipick, '1970-01-01', '2011-03-14')
        # df_clipick = pd.concat([df_clipick_start, df_bias_corr])

        # GET INTRA CORRELATION
        inca_corr = correlation_with_all(df_inca, 'RSS', ['lat','lon'])
        clipick_corr = correlation_with_all(df_clipick, 'RSS')
        data = {'INCA':inca_corr, 'CLIPICK_BC':clipick_corr}
        df_corr = get_corr_df(data)

        # WRITE INTRA CORRELATION TO FILE
        path = 'inca_clipick_bias_corr'
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
        get_plots_for_pair(df_inca, df_clipick, 'Inca', 'Clipick_BC', c,
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
