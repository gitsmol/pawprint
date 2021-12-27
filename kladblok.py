import pawprint
import pandas as pd
import importlib
importlib.reload(pawprint)

data = pawprint.BearableData('../bearable-export-19-12-2021.csv')
# data.categories = data.categories.remove('Factors')
print(data.REP_longform.head(20))
# print(data.REP_longform.dtypes)
data.REP_longform.to_excel('./REP_longform.xlsx')
# selection = data.INT_df['datetime'].isna()
# selection = data.INT_df['datetime'].isna()
# selection = data.INT_df[~(data.INT_df['datetime'] == '')]
# print(selection.value_counts())
