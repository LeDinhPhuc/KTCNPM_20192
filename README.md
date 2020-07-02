# Static Time Forecasting
python times.py [dataset_name]
Eg: python times.py C2013-12

# Static Cost Forecasting
python costs.py [dataset_name]
Eg: python costs.py C2013-12

# EVM cost forecasting
python costs-evm.py [dataset_name]

# Proposed method for cost forecasting
python proposed.py [dataset_name]


By default, the test set is the last 33% of tracking periods. To change the size of the test set, find this line in source code: if t >= (len(tracking_periods)*2/3).

For testing 50% of tracking periods, change that line to if t >= (len(tracking_periods)*1/2)

For testing 25% of tracking periods, change that line to if t >= (len(tracking_periods)*3/4)
