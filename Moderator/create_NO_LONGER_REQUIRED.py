import numpy
import os
import pandas as pd

path = '../../Images'

lis = os.listdir(path)

annot_ids = [-1 for x in lis]

data = pd.DataFrame({'img_list':lis, 'annotator_id' : annot_ids})

data.to_csv('annotation_list.csv', index_col = False)

