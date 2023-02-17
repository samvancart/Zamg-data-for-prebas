import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_column(df, col_name, title, legend='Databases', kind='line'):
    df.plot(x='time',kind=kind, alpha=0.7)
    
    plt.legend(title=legend)

    plt.ylabel(col_name, fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title(title, fontsize=16)

    # plt.show()

def plot_column_xy(df, col_name, title, y, legend='Databases', kind='line', x='time'):
    # df.plot(x='time',kind=kind)
    df.plot(x=x, y=y, kind=kind)
    plt.legend(title=legend)

    plt.ylabel(y, fontsize=14)
    # plt.xlabel('Time', fontsize=14)
    plt.xlabel(x, fontsize=14)
    plt.title(title, fontsize=16)

    # plt.show()


def plot_multile_columns(dfs, column, title=""):
    for df in dfs:
        plt.plot(df[0][column], label=df[1], color='green')
    plt.title(title)
    plt.xlabel("Time")      
    plt.ylabel(column)      
    plt.show()

def show_plot():
    plt.show()

def save_plot_to_file(file):
    plt.savefig(file, dpi=1200)

def create_plot_folder(name):
    newpath = f'plots/{name}' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath