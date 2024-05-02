"""
TODO:
- Understand how to extract full data
"""
import pandas as pd
import json
import re
from typing import List
from batch_framework.filesystem import DropboxBackend
from batch_framework.storage import PandasStorage
data = PandasStorage(DropboxBackend('/data/canon/raw')).download('latest_cache')
def get_requires_dist(x):
    item = x['info']['requires_dist']
    if item is not None:
        return set(item)
    else:
        return item

def get_pip_requires(x):
    if x['info']['pipdeptree'] is not None:
        results = [item['metadata']['name'].replace('_', '-') for item in x['info']['pipdeptree']]
        name = x['info']['name']
        return set([ans.lower() for ans in results if ans != name])
    else:
        return []

################
# Start Target #
################

def process_dist_str(x: str) -> str:
    _x = re.sub(r'\([^()]*\)', '', x).strip()
    _x = re.sub(r'\[[^()]*\]', '', _x).strip()
    _x = _x.split(';')[0].strip().lower()
    return _x

def process(x: List[str]) -> List[str]:
    return set([process_dist_str(item) for item in x])

##############
# End Target #
##############

data['y1y2'] = data.latest.map(json.loads).map(
    lambda x: (get_requires_dist(x), get_pip_requires(x)))

print('Total Data Count:', len(data))
data = data[data['y1y2'].map(lambda x: x[0] is not None)]
print('Number of Data with Y1:', len(data))

data['y1y2'] = data['y1y2'].map(lambda x: (process(x[0]), x[1]))



def get_y1_only(yy):
    y1, y2 = yy
    return set(y1) - set(y2)

def get_score(yy):
    num_y1_only = len(get_y1_only(yy))
    num_y1 = len(yy[0])
    return num_y1_only / num_y1
    
data['y1_only'] = data['y1y2'].map(get_y1_only)

data['score'] = data['y1y2'].map(get_score)
print(data[['y1y2', 'y1_only', 'score']])

remaining = set(data['y1_only'].map(list).sum())
print(len(remaining))
# NOTE: Number of remaining y1_only should be as small as possible
