#!/usr/bin/env python
# coding: utf-8

# In[7]:
import pandas 
import glob
import sys 
import matplotlib.pyplot as plt
from utils import find_column_indices, parse_date, MAPE
from beta_static import beta_static_lookup 

data_file = sys.argv[1]
dfs = pandas.read_excel(f'data/{data_file}.xlsx', sheet_name=None,
    skiprows=1)
sheetnames = list(dfs.keys())

import numpy as np


import os 
if not os.path.isdir("data"):
    os.makedirs("data")
baselines = dfs['Baseline Schedule'][['ID', 'Duration', 'Total Cost']].values
baselines[:,1] = [parse_date(x) for x in baselines[:,1]]
# planned duration
BAC = baselines[0,2]
tracking_periods = [x for x in sheetnames if "TP" in x]
n_tracking_periods = baselines[0,1] / (20*60)
print("BAC:", BAC)
print("Number of tracking periods:", n_tracking_periods)

def cost_forecasting_evm():
    # Col 0 = ID, col 12 = Duration
    beta = beta_static_lookup[data_file]   
    ACs = [0] # init AT0 = 0
    EVs = [0]
    EAC_costs = [] # predict project duration
    start_test = False
    t = 1
    for period in tracking_periods:
        print("Tracking periods:", period)
        cols = find_column_indices(dfs[period].values[1], ["ID", "Actual Cost", "Earned Value (EV)", "Planned Value (PV)"])
        data_period = dfs[period].values[2:, cols] 
        assert (baselines[:,0] == data_period[:,0]).sum() == len(baselines), "Wrong permutation!"

        AC = data_period[0, 1]
        ACs.append(AC)
        EV = data_period[0, 2]
        PV = data_period[0, 3]
        if t >= (len(tracking_periods)*2/3):
        # if True:
            CPI = EV/AC
            EAC = (BAC-EV) / CPI + AC
            print("Predict EAC:", EAC)
            EAC_costs.append(EAC)
        t+=1
    print("Project actual costs: ", data_period[0,1])
    mape, error = MAPE([ACs[-1]]*len(EAC_costs[:-1]), EAC_costs[:-1])
    print("EVM MAPE: ", mape)
    return error, mape


if __name__ == '__main__':
    if not os.path.isdir("figures"):
        os.makedirs("figures")
    fp = open(f"logs/costs/{data_file}.log", "w+")
    fp.write(f"Dataset\tDynamic\n")
    error_static, mape = cost_forecasting_evm()
    fp.write(f"{data_file}\t{mape:.2f}\n")
