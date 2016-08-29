from ggplot import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import requests
from datetime import datetime
import pytz
import time
import csv
import os
from pandas import DataFrame


"""
unlike analysis.py that performs analysis against all Root Servers, this script is intended to do analysis on a single
Root Server. It is useful when one (or some) Root Server has different analysis characteristics and that I am too lazy
to accommodate it in analysis.py
"""

root_list = 'm'
csv_dir = '../Notebook/datasets/'


def get_peer_degree_dist(root):
    directory = '{}{}/'.format(csv_dir, root)
    result4 = {}
    result6 = {}
    for file in sorted(os.listdir(directory)):
        timestamp = int(file.split('-')[0])
        filename = '{}{}'.format(directory, file)
        opened_file = DataFrame.from_csv(filename, sep='\t')
        if not opened_file.empty:
            res4 = opened_file['len4'].value_counts()
            result4[timestamp] = res4
            res6 = opened_file['len6'].value_counts()
            result6[timestamp] = res6
        else:
            result4[timestamp] = pd.Series()
            result6[timestamp] = pd.Series()

    # Plot
    fig, axes = plt.subplots(nrows=2, ncols=1)

    plot_result4 = DataFrame.from_dict(result4, orient='index')
    plot_result6 = DataFrame.from_dict(result6, orient='index')

    plot4 = plot_result4.plot.bar(stacked=True, ax=axes[0], figsize=(14,10), ylim=(0,80), title='IPv4')
    plot6 = plot_result6.plot.bar(stacked=True, ax=axes[1], figsize=(14,10), ylim=(0,80),title='IPv6')

    n = 6

    ticks = plot4.xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%Y-%m-%d') for l in plot4.xaxis.get_ticklabels()]
    plot4.xaxis.set_ticks(ticks[::n])
    plot4.xaxis.set_ticklabels(ticklabels[::n], rotation=25)

    ticks = plot6.xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%Y-%m-%d') for l in plot6.xaxis.get_ticklabels()]
    plot6.xaxis.set_ticks(ticks[::n])
    plot6.xaxis.set_ticklabels(ticklabels[::n], rotation=25)

    plt.savefig('figs/eps/peer_degree_dist_{}.eps'.format(root), format='eps', dpi=1000)
    plt.savefig('figs/png/peer_degree_dist_{}.png'.format(root))

    print('finish: peer degree {}-Root Server'.format(root))


def get_as_path_avg_length(root):
    directory = '{}{}/'.format(csv_dir, root)
    result4 = {}
    result6 = {}
    for file in sorted(os.listdir(directory)):
        timestamp = int(file.split('-')[0])
        filename = '{}{}'.format(directory, file)
        opened_file = DataFrame.from_csv(filename, sep='\t')
        if not opened_file.empty:
            res4 = opened_file['len4']
            res6 = opened_file['len6']
            result4[timestamp] = res4
            result6[timestamp] = res6
        else:
            result4[timestamp] = pd.Series()
            result6[timestamp] = pd.Series()

    plot_result4 = DataFrame.from_dict(result4)
    plot_result6 = DataFrame.from_dict(result6)

    ################
    # Plot
    ################
    fig, axes = plt.subplots(nrows=2, ncols=1)

    plot4 = plot_result4.plot.box(figsize=(14, 10), ax=axes[0], ylim=(1.5, 9.5), title='IPv4')
    plot6 = plot_result6.plot.box(figsize=(14, 10), ax=axes[1], ylim=(1.5, 9.5), title='IPv6')

    n = 6

    ticks = plot4.xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%Y-%m-%d') for l in plot4.xaxis.get_ticklabels()]
    plot4.xaxis.set_ticks(ticks[::n])
    plot4.xaxis.set_ticklabels(ticklabels[::n], rotation=25)

    ticks = plot6.xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%Y-%m-%d') for l in plot6.xaxis.get_ticklabels()]
    plot6.xaxis.set_ticks(ticks[::n])
    plot6.xaxis.set_ticklabels(ticklabels[::n], rotation=25)

    plt.savefig('figs/eps/path_avg_dist_{}.eps'.format(root), format='eps', dpi=1000)
    plt.savefig('figs/png/path_avg_dist_{}.png'.format(root))

    print('finish: path average {}-Root Server'.format(root))

if __name__ == '__main__':
    for root in root_list:
        get_peer_degree_dist(root)
        get_as_path_avg_length(root)
        # get_diff_path_stats(root)