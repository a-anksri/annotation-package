image_folder = '../../Images'
data_file_folder = '../../annotator_data'
annotator = 'Nikhil'
reviewer = 'Ankur'


###Addition in python file

root_config_path = '../../root_config'
if(os.path.exists(root_config_path)):
    f = open(root_config_path, 'r')
    root_config = pickle.load(f)
    f.close()
    annotator_id = root_config['id']
else:
    print('Not Configured. Please Obtain Configuration File')


config_path = '../../config'
if(os.path.exists(config_path)):
    f = open(config_path, 'r')
    config = pickle.load(f)
    f.close()
    cid = config['cid']
    annotator = config['name']
else:
    config = {}
    cid = 0
    annotator = 'Unknown'

#######

import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os

#######

kp_dataset_file = "KEYPOINTS_DATASET_" + annotator_id + '.csv'
status_file = 'STATUS_' + annotator_id + '.csv'
offered_file = 'offered_for_review_' + annotator_id + '_' + cid + '.csv'
offered_record = 'offered_record

#######

kp_dataset_path = os.path.join(data_file_folder, kp_dataset_file)
status_path = os.path.join(data_file_folder, status_file)
offered_path = os.path.join(data_file_folder, offered_file)

#######

kp_dataset = pd.read_csv(kp_dataset_path, index_col = False)
status = pd.read_csv(status_path, index_col = False)


sent = status[status['sent_for_review'] == True ]
sent = sent['file_name'].values
all = status['file_name'].values
complete = status[status['success'] == True]
complete = complete['file_name'].values


for im in all:
     if(( im in sent) or (im not in complete)):
         kp_dataset = kp_dataset[kp_dataset['img_id'] != im]
     else:
         record = status['file_name'] == im
         status.loc[record,'sent_for_review'] = True
     
     



kp_dataset.to_csv(offered_path, index = False)

status.to_csv(status_path, index = False)