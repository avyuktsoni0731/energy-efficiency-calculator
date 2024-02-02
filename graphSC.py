import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

def plot_graph_SC():
    plt.figure(figsize=(10, 6))
    sdx=pd.read_csv('./data/input_sc.csv', usecols=['Voltage']).sort_values(by='Voltage', ascending=True)
    sdy=pd.read_csv('./data/input_sc.csv', usecols=['Current'])

    plt.plot(sdx,sdy)
    plt.xlabel('Voltage')
    plt.ylabel('Current')
    plt.savefig('./static/graphSC.png')