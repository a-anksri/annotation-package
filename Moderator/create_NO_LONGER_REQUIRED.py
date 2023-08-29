import numpy
import os
import pandas as pd

path = '../../Images'

lis = os.listdir(path)

data = pd.DataFrame({'img_list':lis})

data.to_csv('img_list.csv', index_col = False)

