import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_column(df, column, title=""):
    df[column].plot()
    plt.title(title)
    plt.xlabel("Time")      
    plt.ylabel(column)      
    plt.show()

def plot_multile_columns(dfs, column, title=""):
    for df in dfs:
        plt.plot(df[0][column], label=df[1], color='green')
    plt.title(title)
    plt.xlabel("Time")      
    plt.ylabel(column)      
    plt.show()        