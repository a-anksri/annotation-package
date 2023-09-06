import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os

import pickle

root_config_path = '../../annotator_data/root_config'
if(os.path.exists(root_config_path)):
    f = open(root_config_path, 'rb')
    root_config = pickle.load(f)
    f.close()
    annotator_id = root_config['id']
    annotator = root_config['name']
else:
    print('Not Configured. Please Obtain Configuration File')
    
print("Name: " + annotator)
print("Id: {}".format(annotator_id))