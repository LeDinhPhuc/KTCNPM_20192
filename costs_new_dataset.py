#!/usr/bin/env python
# coding: utf-8

# In[7]:

import os
import pandas
import glob
import sys
import matplotlib.pyplot as plt
from utils import find_column_indices, parse_date, MAPE
from beta_static import beta_static_lookup

data_file = sys.argv[1]
dfs = pandas.read_excel(f'new_dataset/{data_file}.xls', sheet_name=None,
                        skiprows=1)
sheetnames = list(dfs.keys())

# In

if not os.path.isdir("data"):
    os.makedirs("data")
# baselines = dfs['Baseline Schedule'][['ID', 'Duration', 'Total Cost']].values
# baselines[:, 1] = [parse_date(x) for x in baselines[:, 1]]
# planned duration
# BAC = baselines[0, 2]
tracking_periods = [x for x in sheetnames if "Sheet1" == x]
# n_tracking_periods = baselines[0, 1] / (20*60)
# print("BAC:", BAC)
# print("Number of tracking periods:", n_tracking_periods)


def cost_forecasting():
    # init trend
    # Ts_AC = [BAC/n_tracking_periods]
    # Ts_EV = [BAC/n_tracking_periods]
    # print("T0_AC = T0_EV: ", Ts_AC[0])

    # Col 0 = ID, col 12 = Duration
    beta = 0.455  # người ta cho dữ liệu rồi, giờ cái mình cần làm là tìm ngược lại beta
    ACs = [0]  # init AC[0] = 0
    t = 1  # biến chạy trong vòng lặp tracking
    EVs = [0]  # khởi tạo mảng EV = [0]
    EAC_costs = []  # predict project duration
    start_test = False  # có làm cái gì với cái này đâu ????
    for period in tracking_periods:  # chỉ có một giai đoạn thôi
        print("Tracking periods:", period)
        cols = find_column_indices(dfs[period].values[1], [
                                   "ID", "PV", "EV", "AC"])
        print("cols ", cols)
        exit(0)
        data_period = dfs[period].values[2:, cols]
        assert (baselines[:, 0] == data_period[:, 0]).sum() == len(
            baselines), "Wrong permutation!"

        # current trend
        cur_AC = data_period[0, 1]
        ACs.append(cur_AC)
        T_AC = beta*(ACs[t] - ACs[t-1]) + (1-beta)*Ts_AC[t-1]
        Ts_AC.append(T_AC)

        EV = data_period[0, 2]
        PV = data_period[0, 3]
        EVs.append(EV)
        T_EV = beta*(EVs[t] - EVs[t-1]) + (1-beta)*Ts_EV[t-1]
        Ts_EV.append(T_EV)

        # if EV < PV and not start_test:
        #     start_test = True
        # if start_test:
        # if t >= (len(tracking_periods)*1/2) and T_EV > 0:
        # if T_EV > 0:
        if t >= (len(tracking_periods)*2/3) and T_EV > 0:
            # if T_EV > 0:
            k = (BAC-EVs[t]) / T_EV
            EAC = ACs[t] + k * T_AC
            EAC_costs.append(EAC)
            print("Predict EAC:", EAC)
        # end calculate
        t += 1
    # print("Project actual costs: ", data_period[0, 1])
    mape, error = MAPE([ACs[-1]]*len(EAC_costs[:-1]), EAC_costs[:-1])
    # print("MAPE: ", mape)
    return error, mape


if __name__ == '__main__':
    if not os.path.isdir("figures"):
        os.makedirs("figures")
    fp = open(f"logs/costs/{data_file}.log", "w+")
    fp.write(f"Dataset: \n")
    error_static, mape = cost_forecasting()
    fp.write(f"{data_file}\t{mape:.2f}\n")
