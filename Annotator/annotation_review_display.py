#Enter folder name where the images and dataset files exist
image_folder = '../../Images'
data_file_folder = '../../annotator_data'
annotator = 'Nikhil'
reviewer = 'Ankur'

#Change if file names are not in the same format as suggested below
keypoints_file = 'KEYPOINTS_DATASET_' + annotator +'.csv'
review_file = 'review_results_' + annotator + '_' + reviewer + '.csv'
status_file = 'STATUS_' + annotator +'.csv'
to_annotate_file = 'to_annotate_' + annotator + '.csv'
report_file = 'report_'+ annotator + '_' + reviewer + '.csv'



window_size = (1028,668)

########

import sys

sys.path.append('..')

#######

import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os
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