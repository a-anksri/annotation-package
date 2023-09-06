import pickle
import os
import sys
#Enter folder name where the images and dataset files exist
image_folder = '../../Images'
data_file_folder = '../../reviewer_data'


###
root_config_path = '../../reviewer_data/root_config'
if(os.path.exists(root_config_path)):
    f = open(root_config_path, 'rb')
    root_config = pickle.load(f)
    f.close()
    reviewer_id = root_config['id']
    reviewer = root_config['name']
else:
    print('Not Configured. Please Obtain Configuration File')
    sys.exit()



###### changed
file_list = os.listdir(data_file_folder)
results_files = {}
count = 0
for file in file_list:
    if file.startswith("offered_for_review"):
        results_files[count] = file
        count += 1

if(len(results_files) == 1):
    keypoints_file = results_files[0]
   
elif(len(results_files) == 0):
    print("No results to review")
    sys.exit()
else:
  print(results_files)
  a = int(input("Enter Sl No of the results file you want to ingest"))
  if(a < 0 or a > len(results_files)):
    print("Invalid input")
    sys.exit()
  keypoints_file = results_files[a]


review_file = 'review_results_{}_'.format(reviewer_id) + keypoints_file

#Change if file names are not in the same format as suggested below
#keypoints_file = 'offered_for_review_' + annotator +'.csv'

to_review_file = "dummy_file.csv"
accepted_file = "ACCEPTED_{}".format(reviewer_id) + '.csv'
expunged_file = "EXPUNGED_{}".format(reviewer_id) + '.csv'

window_size = (1028,668)

import sys

sys.path.append('..')

import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os
from kp_package.annotation_review import *

#Ordinarily, you will not need to change this
#file where keypoint annotations would be saved
kp_dataset_path = os.path.join(data_file_folder, keypoints_file)
#file where list of files to be reviewed will be provided by moderator
to_review_path = os.path.join(data_file_folder, to_review_file)
#file where list of images that have been accepted after review shall be saved. Not required for annotation_tool
review_file_path = os.path.join(data_file_folder, review_file)
accepted_file_path = os.path.join(data_file_folder, accepted_file)
expunged_file_path = os.path.join(data_file_folder, expunged_file)

if(__name__ == '__main__'):
    
    while(True):
        review(kp_dataset_path, accepted_file_path, to_review_path, review_file_path, expunged_file_path, window_size = window_size, image_folder = image_folder, reviewer = reviewer )


        kp_dataset = pd.read_csv(kp_dataset_path, index_col = False)
        
        results_dataset = pd.read_csv(review_file_path, index_col = False)

        kp_files = kp_dataset['img_id'].values
        result_files = results_dataset['img_id'].values
        count = 0
        for im in kp_files:
            if(im not in result_files):
                count += 1

        
        x = 'n'
        if(count == 0):
            os.remove(kp_dataset_path)
            print("Review for " + keypoints_file + " completed. The file has been deleted")

        else:
            print("ALERT: All offered images have not been annotated. Run program again to complete")
            x = input("Complete Review now? (y/n) ")
        if(x == 'y') or (x == 'Y'):
            continue
        else:
            break
        
        