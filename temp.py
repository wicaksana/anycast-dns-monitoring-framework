import os
import pandas as pd
from pandas import DataFrame
from pprint import pprint
from collections import defaultdict
from datetime import datetime
"""
    get required data for stacked bar visualization
    expected output:
    [{
        x: [],
        y: [],
        name: <name>,
        type: 'bar',
    }, {...}]
"""

root = 'a'

container4 = {}
container6 = {}

for file in sorted(os.listdir('datasets/c/')):
    timestamp = int(file.split('-')[0])
    filename = 'datasets/c/{}'.format(file)
    opened_file = DataFrame.from_csv(filename, sep='\t')
    if not opened_file.empty:
        res4 = opened_file['len4']
        res6 = opened_file['len6']
        container4[timestamp] = res4
        container6[timestamp] = res6
    else:
        container4[timestamp] = pd.Series()
        container6[timestamp] = pd.Series()

df4 = DataFrame.from_dict(container4)
df6 = DataFrame.from_dict(container6)

# ts = [datetime.fromtimestamp(i).strftime('%Y-%m-%d') for i in sorted(container4)]

dict4 = defaultdict()
dict6 = defaultdict()

# for key in ts:

for ts in df4:
    # temp_res = dict()
    # a = plot_result4[ts].dropna()
    # print(a)
    dict4[ts] = {
        'name': datetime.fromtimestamp(ts).strftime('%Y-%m-%d'),
        'type': 'box',
        'y': [int(i) for i in df4[ts].dropna()]
    }

pprint(dict4)


