#!/usr/bin/env python
# coding: utf-8

# In[7]:
import pandas 
import glob
import sys 
import matplotlib.pyplot as plt
import os
from utils import parse_date
from beta_static import beta_static_lookup 

col2idx = "name tracking_from tracking_to pv ev ac es".split()
col2idx = {k: i for i, k in enumerate(col2idx)}
# {'name': 0, 'tracking_from': 1, 'tracking_to': 2, 'pv': 3, 'ev': 4, 'ac': 5, 'es': 6}
data_file = sys.argv[1]
dfs = pandas.read_excel(f'data/{data_file}.xlsx', sheet_name=None,
    skiprows=1)
print(type(dfs))
sheetnames = list(dfs.keys())

import numpy as np
def MAPE(ytrue, ypred):
    ytrue = np.array(ytrue) 
    ypred = np.array(ypred)
    error = np.abs((ytrue-ypred)/ytrue) * 100
    mean_error = np.mean(error)
    return mean_error, error

# In[9]:

import os 
if not os.path.isdir("data"):
    os.makedirs("data")
baselines = dfs['Baseline Schedule'][['ID', 'Duration', 'Total Cost']].values

baselines[:,1] = [parse_date(x) for x in baselines[:,1]]
# planned duration

n_actual_tps = len([x for x in sheetnames if "TP" in x])
data = dfs["Tracking Overview"].values
tracking_start_date = data[0, col2idx['tracking_from']]
tracking_end_date = data[-1, col2idx['es']]
PD = (tracking_end_date - tracking_start_date).days
print(f"PD tracking from {tracking_start_date} - {tracking_end_date}: {PD} days")

def get_actual_time(tp_from, tp_to):
    return (tp_to-tp_from).days

def time_forecasting():
    n_expected_tps = PD / 20
    ats = [0]
    tats = [PD/n_expected_tps]
    ess = [0]
    tess = [PD/n_expected_tps]
    beta = beta_static_lookup[data_file]
    peacs = []
    start_test = False
    for t in range(1, n_actual_tps+1):
        duration = get_actual_time(data[t-1, col2idx['tracking_from']], data[t-1, col2idx['tracking_to']]) 
        ats.append(ats[-1]+duration)
        duration = 1 # do not scale duration
        tat = beta*((ats[t]-ats[t-1])/duration) + (1-beta)*tats[t-1]
        tats.append(tat)

        es = data[t-1, col2idx['es']]
        es = PD - (tracking_end_date - es).days
        
        ess.append(es)
        tes = beta*((ess[t]-ess[t-1])/duration) + (1-beta)*tess[t-1]
        tess.append(tes)

        ev = data[t-1, col2idx['ev']]
        pv = data[t-1, col2idx['pv']]
        # if ev < pv and not start_test:
        if t >= (n_actual_tps*1/2):
        # if t >= (n_actual_tps*2/3):
        # if t >= 0:
            start_test = True
        if not start_test: continue
        k = (PD-ess[t])/tes
        eac = ats[t] + k*tat
        # print(f"TP {t} - pEAC {eac:.3f} - k {k:.3f} - tat {tat:.3f}")
        print(f"TP {t} - pEAC={eac:.3f}")
        peacs.append(eac)
    print(f"Actual EAC {ats[-1]:.3f}")
    mape, error = MAPE([ats[-1]]*len(peacs[:-1]), peacs[:-1])
    print(f"MAPE: {mape:.2f}")
    if not os.path.isdir("logs/times/"):
        os.makedirs("logs/times")
    with open(f"logs/times/{data_file}.log", "w+") as fp:
        fp.write(f"Dataset\tStatic\n")
        fp.write(f"{data_file}\t{mape:.2f}")

if __name__ == '__main__':
    time_forecasting()