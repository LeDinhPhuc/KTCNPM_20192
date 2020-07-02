import numpy as np
def find_column_indices(columns , cols_filter):
  return [np.where(columns == c)[0][0] for c in cols_filter]

def parse_date(date):
    elms = date.split()
    total_hour = 0
    for elm in elms:
        if elm.endswith("d"):
            total_hour += int(elm[:-1])*24
        elif elm.endswith("h"):
            total_hour += int(elm[:-1])
    return total_hour

def MAPE(ytrue, ypred):
    ytrue = np.array(ytrue) 
    ypred = np.array(ypred)
    error = np.abs((ytrue-ypred)/ytrue) * 100
    mean_error = np.mean(error)
    return mean_error, error