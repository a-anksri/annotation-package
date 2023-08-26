#Enter folder name where the images and dataset files exist
image_folder = '../../Images'
data_file_folder = '../../annotator_data'
annotator = 'Nikhil'
to_annotate_file = 'to_annotate_' + annotator + '.csv'
keypoints_file = 'KEYPOINTS_DATASET_' + annotator + '.csv'
status_file = 'STATUS_' + annotator + '.csv'

window_size = (1028,668)

#######

import sys

sys.path.append('..')

#######

import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os
from kp_package.annotation_tool import *
from kp_package.annotation_display import see_annot

########

#Ordinarily, you will not need to change this
#file where keypoint annotations would be saved
data_file_path = os.path.join(data_file_folder, keypoints_file)
#file where all images that have been annotated will be saved
status_file_path = os.path.join(data_file_folder, status_file)
#file where list of files to be annotated will be provided by moderator
to_annotate_path = os.path.join(data_file_folder, to_annotate_file)


########

if(__name__ == "__main__"):
    
    if(os.path.exists(to_annotate_path)):
      #If list of images to be annotated has been provided
      tmp = pd.read_csv(to_annotate_path)
      file_names = tmp['img_id'].values
    else:
      #else take all images from the images folder
      file_names = os.listdir(image_folder)
    

    if(os.path.exists(data_file_path)):
      #If some annotations are already done, load them
      data = pd.read_csv(data_file_path, index_col = False)
    else:
      #Create a new empty dataframe to store annotations and save it to a file
      data = pd.DataFrame(columns = ['id', 'pid', 'type', 'x', 'y', 'attr', 'person', 'img_id', 'hidden'])
      data.to_csv(data_file_path, index = False)
    
    if(os.path.exists(status_file_path)):
      #If status file exists, load it
      completed = pd.read_csv(status_file_path, index_col = False)
    else:
      #Else create a new empty datasframe and save it to a file
      completed = pd.DataFrame(columns = ['file_name','annotator','success', 'sent_for_review', 'accepted', 'reviewer_remarks', 'reviewer', 'expunge'])
      completed.to_csv(status_file_path, index = False)
    
    #To skip already annotated images. Only considers those entries which were completed successfully 
    completed_files = completed[completed['success'] == True]
    completed_files = completed_files['file_name'].values
    all_files = completed['file_name'].values
    expunged_files = completed[completed['expunge'] == True]
    expunged_files = expunged_files['file_name'].values
    
    
    for file_name in file_names:

      #To skip annotated images and non image files
      if(file_name  in completed_files) or (file_name in expunged_files) or (not (file_name.endswith('.png'))):
        continue

      file_path = os.path.join(image_folder, file_name)
      All_annotations = Final_Annotation()
    
      img = cv.imread(file_path)
      if(file_name in all_files):
          see_annot(data_file_path, status_file_path, window_size, image_folder, data_file_folder, file_name)
    
      data = pd.read_csv(data_file_path, index_col = False)
      this_rec = data[data['img_id'] == file_name]
      if(len(this_rec) == 0):
            next_id = 0
      else:
          num = this_rec['person'].values
          if(len(num) == 0):
            next_id = 0
          else:
            next_id = max(num) + 1
      
      added = tool_GUI(file_name, All_annotations, name = file_name, img = img, window_size = window_size, next_id = next_id)
      
      new_file = pd.DataFrame({'file_name':[file_name], 'annotator':[annotator], 'success':[False], 'sent_for_review':[False], 'accepted':[False], 'reviewer_remarks':["Nil"], 'reviewer':["Nil"], 'expunge':[False]})
      if(file_name not in all_files):
        completed = completed.append(new_file, ignore_index = True)
      
      completed.to_csv(status_file_path, index = False) 
  
        
            
         
      
      if(added):
          a = All_annotations.annotations
          add = pd.DataFrame(a)

          data = data.append(add, ignore_index = True)
          
          

          #file operations begin. Ensure integrity
          
          tmp_path = os.path.join(data_file_folder, 'tmp_keypoints_dataset.csv')
          data.to_csv(tmp_path, index = False)
          os.remove(data_file_path)
          os.rename(tmp_path,data_file_path)
        
          inp = input("Want to review annotations for this image? (y/n) ")
          if(inp == 'y'):
                see_annot(data_file_path, status_file_path, window_size, image_folder, data_file_folder, file_name)


          q = input('Mark this image as completed? You will not be able to annotate this image further if marked completed (y/n) ')
          if(q == 'y'):
                    this_record = completed['file_name'] == file_name
                    completed.loc[this_record,'success'] = True
                    print("Image " + file_name + " completed")
          else:
                    print("Image " + file_name + " kept as Incomplete. You can add further annotations when your run the code next time")
          
          #data stored in temp file

          

          
          
          #File operations completed

          
      else:
        if(len(this_rec) == 0):
                        completed = completed[completed['file_name'] != file_name]
                        print("No remaining Annotations for {}. Status Record Expunged".format(file_name))
        else:            
            q = input('No annotation added. Still mark this image as completed? You will not be able to annotate this image further if marked completed (y/n) ')
            if(q == 'y'):
                    this_record = completed['file_name'] == file_name
                    completed.loc[this_record,'success'] = True
                    print("Image " + file_name + " completed")
                    this_rec = data[data['img_id'] == file_name]

                        
          
      
      completed.to_csv(status_file_path, index = False)
      inp = input("Enter 'y' to go to next image, 'n' to quit ")
            
      
    
      if(inp == 'y'):
        continue
      else:
        break

      print(completed['file_name'].values)


