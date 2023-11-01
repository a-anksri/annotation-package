import os
import pickle
import sys
import pandas as pd

def write(mode, obj, file, create = False):
    tmp_made = False
    
    if(not (os.path.exists(file)) and not create):
            return(False)
        
    tmp_path = '../../annotator_data/tmp_file'
    
    if(mode == 'pandas'):
        
        #try:
            
            obj.to_csv(tmp_path, index = False)
           
            tmp_made = True
            if(os.path.exists(file)):
                os.remove(file)
            
            os.rename(tmp_path, file)
            
            return(True, tmp_made)
            '''
        except(IOError):
            if(tmp_made):
                print("IO ERROR while writing to {}: Data dumped in tmp file".format(tmp_path))
                
            else:
                print("IO: ERROR while writing to {}: Could not write".format(tmp_path))
            return(False)
            '''
        
    elif(mode == 'pickle'):
        try:
            f = open(tmp_path, 'wb')
            pickle.dump(obj, f)
            tmp_made = True
            f.close()
            if(os.path.exists(file)):
                os.remove(file)
            
            os.rename(tmp_path, file)
            return(True, tmp_made)
        except:
            if(tmp_made):
                print("IO ERROR: Data dumped in tmp file")
            else:
                print("IO: ERROR: Could not write")
            return(False)
        
def read(mode, obj, file):
    pass
            