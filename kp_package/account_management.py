import pickle
import os
import sys

#Code for Account Management

def start():
    io_ok = False
    lock = False
    config_ok = False
    cid = 0
    

    root_config_path = '../../annotator_data/root_config'
    if(os.path.exists(root_config_path)):
        f = open(root_config_path, 'rb')
        root_config = pickle.load(f)
        f.close()
        annotator_id = root_config['id']
        annotator = root_config['name']
        io_ok =True
        
    
        
        
        

    config_path = '../../annotator_data/config'

    if(os.path.exists(config_path)):
        f = open(config_path, 'rb')
        config = pickle.load(f)

        image_folder = config.get('im_pth', '../../../Images')
        cid = config.get('cid',0)
        f.close()
        config_ok = True
    
        

    locked_path = '../../annotator_data/locked'
    if(os.path.exists(locked_path)):
        pass
        
    else:
        tmp = {}
        f = open(locked_path, 'wb')
        lock = True
        pickle.dump(tmp,f)
        f.close()
    
    return(io_ok, lock, config_ok, annotator_id, annotator, config)

def stop():
    locked_path = '../../annotator_data/locked'
    os.remove(locked_path)
    
