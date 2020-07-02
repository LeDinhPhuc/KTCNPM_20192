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

def dynamic_cost():
    # init trend
    Ts_AC = [BAC/n_tracking_periods]
    Ts_EV = [BAC/n_tracking_periods]
    init_T = BAC/n_tracking_periods
    print("T0_AC = T0_EV: ", Ts_AC[0])

    def select_best_beta(cur_AC):
        betas = [] # list of tuples (beta, MAPE)
        for beta in np.arange(0.0, 1, 0.05): # e^beta*x
            _ACs = [0]
            _Ts_AC = [0]
            predict_ACs = []
            for prev_period in range(0, cur_period):
                # predict AC of current period, cur_AC = prev_AC + trend_AC
                data_prev_period = dfs[tracking_periods[prev_period]].values[2:, cols]
                prev_AC = data_prev_period[0, 1]
                _ACs.append(prev_AC)
                _T_AC = calculate_current_trend(_ACs, beta, init_T)
                predict_AC = _ACs[prev_period-1] + (cur_period - prev_period)*_T_AC
                predict_ACs.append(predict_AC)
            if len(predict_ACs) == 0:
                error = 0
            else:
                ytrue = np.array([cur_AC]*len(predict_ACs))
                ypred = np.array(predict_ACs)
                error = np.abs((ytrue-ypred)/ytrue) * 100
                weights = 1 - np.arange(0, 1, 1/len(error))[:len(error)]
                # weights = np.zeros(len(error))
                # weights[-1] = 1
                error = np.sum(error*weights)
            betas.append((beta, error))
        # select best beta
        beta = sorted(betas, key=lambda x: x[1])[0][0]
        return beta

    def calculate_current_trend(ACs, beta, init_T):
        # ACs[0] must be equals to 0
        if len(ACs) == 1: return init_T
        prev_T = calculate_current_trend(ACs[:-1], beta, init_T)
        T = beta*(ACs[-1] - ACs[-2]) + (1-beta) * prev_T
        return T

    # Col 0 = ID, col 12 = Duration
    ACs = [0] # init AT0 = 0
    t = 1
    EVs = [0]
    EAC_costs = [] # predict project duration
    start_test = False
    cols = find_column_indices(dfs[tracking_periods[0]].values[1], ["ID", "Actual Cost", "Earned Value (EV)", "Planned Value (PV)"])
    betas = []
    for cur_period, period in enumerate(tracking_periods):
        print("=== Tracking periods:", period)
        data_period = dfs[period].values[2:, cols]
        cur_AC = data_period[0, 1]
        ACs.append(cur_AC)
        # find optimal beta
        beta = select_best_beta(cur_AC)
        print(f"Best beta {beta:.3f}", )
        # current trend
        # T_AC = beta*(ACs[t] - ACs[t-1]) + (1-beta)*Ts_AC[t-1]
        T_AC = calculate_current_trend(ACs, beta, init_T)
        Ts_AC.append(T_AC)

        EV = data_period[0,2]
        PV = data_period[0,3]
        EVs.append(EV)
        T_EV = beta*(EVs[t] - EVs[t-1]) + (1-beta)*Ts_EV[t-1]
        Ts_EV.append(T_EV)

        # if EV < PV and not start_test:
        #     start_test = True
        # if start_test:
        if t >= (len(tracking_periods)*2/3) and T_EV > 0:
        # if T_EV > 0:
            betas.append(beta)
            k = (BAC-EVs[t]) / T_EV
            EAC = ACs[t] + k * T_AC
            EAC_costs.append(EAC)
            print(f"Predict EAC: {EAC:.3f}")
        # end calculate
        t += 1
    print("Project actual costs: ", ACs[-1])
    mape, error = MAPE([ACs[-1]]*len(EAC_costs[:-1]), EAC_costs[:-1])
    print(f"Dynamic MAPE: {mape:.2f}")
    return error, mape, ACs[-len(error):], EAC_costs[:-1], betas[:-1]

if __name__ == '__main__':
    if not os.path.isdir("figures"):
        os.makedirs("figures")
    fp = open(f"logs/costs/{data_file}.log", "w+")
    fp.write(f"Dataset\tDynamic\n")
    error_dyn, mape_dyn, acs, eacs_predict, betas = dynamic_cost()
    fp.write(f"{data_file}\t{mape_dyn:.2f}\n")
