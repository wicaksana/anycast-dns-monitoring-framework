import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm
from datetime import datetime
import os
from pandas import DataFrame
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.code import Code
import numpy as np

root_list = 'acdfijklm'
# root_list = 'ac'
csv_dir = '../Notebook/datasets/'


# def get_peer_degree_dist(root):
#     directory = '{}{}/'.format(csv_dir, root)
#     result4 = {}
#     result6 = {}
#     for file in sorted(os.listdir(directory)):
#         timestamp = int(file.split('-')[0])
#         filename = '{}{}'.format(directory, file)
#         opened_file = DataFrame.from_csv(filename, sep='\t')
#         if not opened_file.empty:
#             res4 = opened_file['len4'].value_counts()
#             result4[timestamp] = res4
#             res6 = opened_file['len6'].value_counts()
#             result6[timestamp] = res6
#         else:
#             result4[timestamp] = pd.Series()
#             result6[timestamp] = pd.Series()
#
#     ################
#     # Plot
#     ################
#     fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, sharey=True)
#
#     plot_result4 = DataFrame.from_dict(result4, orient='index')
#     plot_result6 = DataFrame.from_dict(result6, orient='index')
#
#     # re-order dataframe column
#     plot_result4 = plot_result4.sort_index(axis=1)
#     plot_result6 = plot_result6.sort_index(axis=1)
#
#     plot4 = plot_result4.plot.bar(stacked=True,
#                                   ax=axes[0],
#                                   figsize=(14,6),
#                                   width=1.0,
#                                   alpha=0.7)
#     plot6 = plot_result6.plot.bar(stacked=True,
#                                   ax=axes[1],
#                                   figsize=(14,6),
#                                   width=1.0,
#                                   alpha=0.7)
#
#     n = 6
#
#     axes[0].text(0.5, 0.9, 'IPv4', fontsize=20, horizontalalignment='center', verticalalignment='center', transform= axes[0].transAxes, bbox={'facecolor': 'white', 'pad': 5})
#     axes[1].text(0.5, 0.9, 'IPv6', fontsize=20, horizontalalignment='center', verticalalignment='center', transform= axes[1].transAxes, bbox={'facecolor': 'white', 'pad': 5})
#     axes[0].grid(True)
#     axes[1].grid(True)
#
#     ticks = axes[1].xaxis.get_ticklocs()
#     ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%d/%m/%y') for l in
#                   axes[1].xaxis.get_ticklabels()]
#     axes[1].xaxis.set_ticks(ticks[::n])
#     axes[1].xaxis.set_ticklabels(ticklabels[::n], rotation=0)
#
#     plt.tight_layout()
#     plt.savefig('figs/eps/peer_degree_dist_{}.eps'.format(root), format='eps', dpi=1000)
#     plt.savefig('figs/png/peer_degree_dist_{}.png'.format(root))
#
#     print('finish: peer degree {}-Root Server'.format(root))


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

    ################
    # Plot
    ################
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)

    plot_result4 = DataFrame.from_dict(result4, orient='index')
    plot_result6 = DataFrame.from_dict(result6, orient='index')

    # re-order dataframe column
    plot_result4 = plot_result4.sort_index(axis=1)
    plot_result6 = plot_result6.sort_index(axis=1)

    # normalize to scale [0, 1]
    col_list = plot_result4.columns
    for item in plot_result4.iterrows():
        total = item[1].sum()
        for col in col_list:
            item[1][col] = item[1][col] / total

    col_list = plot_result6.columns
    for item in plot_result6.iterrows():
        total = item[1].sum()
        for col in col_list:
            item[1][col] = item[1][col] / total

    # plot
    plot4 = plot_result4.plot.bar(stacked=True,
                                  ax=axes[0],
                                  ylim=(0,1),
                                  figsize=(14,6),
                                  width=1.0,
                                  alpha=0.7)
    plot6 = plot_result6.plot.bar(stacked=True,
                                  ax=axes[1],
                                  ylim=(0, 1),
                                  figsize=(14,6),
                                  width=1.0,
                                  alpha=0.7)

    n = 6

    axes[0].text(0.5, 0.9, 'IPv4', fontsize=20, horizontalalignment='center', verticalalignment='center', transform= axes[0].transAxes, bbox={'facecolor': 'white', 'pad': 5})
    axes[1].text(0.5, 0.9, 'IPv6', fontsize=20, horizontalalignment='center', verticalalignment='center', transform= axes[1].transAxes, bbox={'facecolor': 'white', 'pad': 5})
    axes[0].grid(True)
    axes[1].grid(True)

    ticks = axes[1].xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%d/%m/%y') for l in
                  axes[1].xaxis.get_ticklabels()]
    axes[1].xaxis.set_ticks(ticks[::n])
    axes[1].xaxis.set_ticklabels(ticklabels[::n], rotation=0)

    plt.tight_layout()
    plt.savefig('figs/eps/peer_degree_dist_{}.eps'.format(root), format='eps', dpi=1000)
    plt.savefig('figs/png/peer_degree_dist_{}.png'.format(root))

    print('finish: peer degree {}-Root Server'.format(root))


def get_as_path_avg_length(root):
    # read this: http://matplotlib.org/examples/pylab_examples/subplots_demo.html
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
    fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True)

    plot4 = plot_result4.plot.box(figsize=(14, 5), ax=axes[0], ylim=(1.5, 9.5))
    plot6 = plot_result6.plot.box(figsize=(14, 5), ax=axes[1], ylim=(1.5, 9.5))

    n = 6

    # ticks = plot4.xaxis.get_ticklocs()
    # ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%d/%m/%y') for l in plot4.xaxis.get_ticklabels()]
    # plot4.xaxis.set_ticks(ticks[::n])
    # plot4.xaxis.set_ticklabels(ticklabels[::n], rotation=25)
    axes[0].text(3, 8, 'IPv4', fontsize=20, bbox={'facecolor': 'white', 'pad': 5})
    axes[1].text(3, 8, 'IPv6', fontsize=20, bbox={'facecolor': 'white', 'pad': 5})
    axes[0].grid(True)
    axes[1].grid(True)

    ticks = axes[1].xaxis.get_ticklocs()
    ticklabels = [datetime.fromtimestamp(int(l.get_text())).strftime('%d/%m/%y') for l in axes[1].xaxis.get_ticklabels()]
    axes[1].xaxis.set_ticks(ticks[::n])
    axes[1].xaxis.set_ticklabels(ticklabels[::n], rotation=25)

    plt.tight_layout()
    plt.savefig('figs/eps/path_avg_dist_{}.eps'.format(root), format='eps', dpi=1000)
    plt.savefig('figs/png/path_avg_dist_{}.png'.format(root))

    print('finish: path average {}-Root Server'.format(root))


def get_peers_composition(root):
    """
    draw graphs of peers composition (identical, different path, shorter IPv4, shorter IPv6)
    :param root:
    :return:
    """
    reducer = Code("""
        function(obj, prev) {
            if(obj.path4.length > obj.path6.length) {
                prev.ipv6_shorter++;
            }
            else if(obj.path4.length < obj.path6.length) {
                prev.ipv4_shorter++;
            }
            else if(obj.path4.length == obj.path6.length) {
                if(obj.path4.toString() == obj.path6.toString()) {
                    prev.identical++;
                } else {
                    prev.different_path++;
                }
            }
        }
    """)

    container = {}
    fig, axes = plt.subplots()

    coll = anycast['{}_root'.format(root)]
    res = coll.group(key={'timestamp': 1},
                     condition={},
                     initial={'identical': 0, 'different_path': 0, 'ipv4_shorter': 0, 'ipv6_shorter': 0},
                     reduce=reducer)

    # normalise the timestamp
    container[root] = DataFrame(res)
    container[root]['timestamp'] = pd.to_datetime(container[root]['timestamp'] * 1000000000)
    container[root] = container[root].set_index(['timestamp'])

    for item in container[root].iterrows():
        total = item[1]['identical'] + item[1]['different_path'] + item[1]['ipv4_shorter'] + item[1]['ipv6_shorter']
        item[1]['identical'] = item[1]['identical'] / total
        item[1]['different_path'] = item[1]['different_path'] / total
        item[1]['ipv4_shorter'] = item[1]['ipv4_shorter'] / total
        item[1]['ipv6_shorter'] = item[1]['ipv6_shorter'] / total

    # bar plot
    bars = container[root].plot.bar(stacked=True,
                                    ax=axes,
                                    figsize=(14, 2.5),
                                    width=1.0,
                                    alpha=0.7,
                                    ylim=(0, 1))

    # display total of peers at the top of bins
    temp_set = set()
    for bar in bars.patches:
        temp_set.add(bar.get_x())
    temp_list = sorted(list(temp_set))

    for idx, item in enumerate(res):
        total = item['identical'] + item['ipv4_shorter'] + item['ipv6_shorter'] + item['different_path']
        axes.text(temp_list[idx] + 0.5,
                  1.025,
                  int(total),
                  horizontalalignment='center',
                  verticalalignment='bottom',
                  fontsize=8,
                  rotation=90)

    n = 6

    axes.grid(True)

    ticks = axes.xaxis.get_ticklocs()
    ticklabels = [format_date(l.get_text()) for l in axes.xaxis.get_ticklabels()]
    axes.xaxis.set_ticks(ticks[::n])
    axes.xaxis.set_ticklabels(ticklabels[::n], rotation=0)
    axes.set_xlabel('')
    axes.legend().set_visible(False)

    print('finish')

    # legend
    plt.legend(loc='lower center',
               bbox_to_anchor=(0.2, 0.12, 0.6, 0.6),
               bbox_transform=plt.gcf().transFigure,
               ncol=4,
               mode='expand',
               )
    plt.tight_layout()

    plt.savefig('figs/eps/peer_composition_{}.eps'.format(root), format='eps', dpi=1000)
    plt.savefig('figs/png/peer_composition_{}.png'.format(root))

    print('finish: peer composition {}-Root Server'.format(root))


def get_convergence_stats(root):
    """
    draw graphs of convergence
    :return:
    """
    print('get_convergence_stats: {}-Root'.format(root))
    reducer = Code("""
        function(obj, prev) {
            if(obj.path4.toString() != obj.path6.toString()) {
                prev.different++;
            } else {
                prev.identical++;
            }
        }
    """)

    coll = anycast['{}_root'.format(root)]
    res = coll.group(key={'timestamp': 1}, condition={}, initial={'identical': 0, 'different': 0}, reduce=reducer)
    container = DataFrame(res)

    container['timestamp'] = pd.to_datetime(container['timestamp'] * 1000000000)
    container = container.set_index(['timestamp'])

    container['total'] = pd.Series()
    container['diff_pct'] = pd.Series()
    container['ident_pct'] = pd.Series()

    for item in container.iterrows():
        item[1]['total'] = item[1]['different'] + item[1]['identical']
        item[1]['diff_pct'] = item[1]['different'] / item[1]['total']
        item[1]['ident_pct'] = item[1]['identical'] / item[1]['total']

    fig, ax = plt.subplots()
    # fig.text(0, 0.5, 'Percentage (%)', va='center', rotation='vertical')
    # fig.text(1, 0.5, 'Amount of peers', va='center', rotation='vertical')

    ax2 = ax.twinx()
    container['ident_pct'].plot(ylim=(0, 1),
                                xlim=(pd.Timestamp('2008-02-1'), pd.Timestamp('2016-06-01')),
                                ax=ax,
                                figsize=(6, 4),
                                label='pct (%)')
    ax2.tick_params(axis='y', colors='#FF1493')

    container['total'].plot(color='r',
                            alpha=0.35,
                            ylim=(0, 120),
                            xlim=(pd.Timestamp('2008-02-1'), pd.Timestamp('2016-06-01')),
                            ax=ax2,
                            figsize=(6, 4),
                            label="peers")

    ax.grid(True)
    ax.set_xlabel('')
    ax.tick_params(axis='y', colors='blue')

    plt.tight_layout()
    fig.savefig('figs/eps/convergence_over_time_{}.eps'.format(root), format='eps', dpi=1000)
    fig.savefig('figs/png/convergence_over_time_{}.png'.format(root))

    print('finish')


def get_path_avg():
    """
    TODO: do this
    :return:
    """
    pass
########################################################################################################################
# Helper methods
########################################################################################################################


def format_date(dt):
    try:
        dt = dt.split(' ')[0]
        year, month, day = dt.split('-')
        returned = day + '/' + month + '/' + year[2:]
    except ValueError:
        returned = dt
        print('error: {}'.format(dt))
    return returned


def dateparse(time_in_secs):
    return datetime.fromtimestamp(float(time_in_secs))


if __name__ == '__main__':
    client = MongoClient()
    anycast = client.anycast_monitoring

    for r in root_list:
        # get_peer_degree_dist(r)
        # get_as_path_avg_length(r)
        get_peers_composition(r)
        # get_convergence_stats(r)