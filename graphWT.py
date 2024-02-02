import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

def plot_graph_WT():
    plt.figure(figsize=(10,6))
    x=pd.read_csv('./data/input_wt.csv', usecols=['Wind speed m/s'])
    y=pd.read_csv('./data/output_wt.csv', usecols=['Efficiency'])

    plt.plot(x,y)
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Efficiency (in %)')
    plt.savefig('./static/graphWT.png')
    