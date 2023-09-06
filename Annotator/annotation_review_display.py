import pickle
import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os


#Enter folder name where the images and dataset files exist
image_folder = '../../Images'
data_file_folder = '../../annotator_data'

#######Added in py file

root_config_path = '../../annotator_data/root_config'
if(os.path.exists(root_config_path)):
    f = open(root_config_path, 'rb')
    root_config = pickle.load(f)
    f.close()
    annotator_id = root_config['id']
    annotator = root_config['name']
else:
    print('Not Configured. Please Obtain Configuration File')

#Change if file names are not in the same format as suggested below
keypoints_file = 'KEYPOINTS_DATASET_{}'.format(annotator_id) +'.csv'

file_list = os.listdir(data_file_folder)
results_files = {}
count = 0
for file in file_list:
    if "review_results" in file:
        results_files[count] = file
        count += 1

if(len(results_files) == 1):
    review_file = results_files[0]
elif(len(results_files) == 0):
    print("No results to ingest")
    sys.exit()
else:
  print(results_files)
  a = int(input("Enter Sl No of the results file you want to ingest"))
  if(a < 0 or a > len(results_files)):
    print("Invalid input")
    sys.exit()
  review_file = results_files[a]

status_file = 'STATUS_{}'.format(annotator_id) +'.csv'
to_annotate_file = 'to_annotate_{}'.format(annotator_id) + '.csv'
report_file = 'report_'+ review_file



window_size = (1028,668)

########

import sys

sys.path.append('..')

#######

from kp_package.annotation_display import *
#######






#Ordinarily, you will not need to change this
#file where keypoint annotations would be saved
kp_dataset_path = os.path.join(data_file_folder, keypoints_file)
status_file_path = os.path.join(data_file_folder, status_file)

#file where list of images that have been accepted after review shall be saved. Not required for annotation_tool
review_file_path = os.path.join(data_file_folder, review_file)
#file where list of files to be annotated will be provided by moderator
to_annotate_path = os.path.join(data_file_folder, to_annotate_file)

#######

if(__name__ == '__main__'):
    see_review(kp_dataset_path, status_file_path, review_file_path, window_size, image_folder, data_file_folder)
    print("Complete: The results file has been deleted")
    os.remove(review_file_path)