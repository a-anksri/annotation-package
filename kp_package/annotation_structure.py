import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os



landmarks = ["Root", "Forehead", "Left Eye", "Left Ear", "Left Shoulder", "Left Hip", "Right Eye", "Right Ear", "Right Shoulder", "Right Hip", "Nose", "Left Elbow", "Left Knee", "Right Elbow", "Right Knee", "Left Wrist", "Left Ankle", "Right Wrist", "Right Ankle", "Mouth", "Crown"]
limbs = {"Root":[1], "Forehead":[10,19,2,6,3,7,20,4,8,5,9], "Left Shoulder":[11], "Left Elbow": [15], "Left Hip":[12], "Left Knee": [16], "Right Shoulder":[13], "Right Elbow": [17], "Right Hip":[14], "Right Knee": [18]}
possible_duplicates = [1,11,12,13,14]
annotation_types = ["Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Point", "Bbox", "Bbox", "Bbox", "Bbox"]


class Link:

  def __init__(self, landmark, possible = False, annotation_type = "Point"):
    self.landmark_type = landmark
    self.parent = self
    self.children = []
    self.next_child = 0
    self.duplicate_possible = possible
    self.touched = False
    self.annotation_type = annotation_type
  
  def add_parent(self, parent):
    self.parent = parent

  def add_child(self, child):
    self.children.append(child)

  def get_type(self):
    return self.landmark_type

  def get_parent(self):
    return self.parent

  def get_annotation_type(self):
      return self.annotation_type

  def check_over(self):
    if(self.next_child == len(self.children)):
      
      return(True)
    else:
      return(False)
  
  

class Chain:

  def __init__(self, landmarks, limbs, possible_duplicates, annotation_types):
    self.landmarks = landmarks
    self.limbs = limbs
    self.possible_duplicates = possible_duplicates
    self.annotation_types = annotation_types
    self.links = {}
    print(self.landmarks)
 
    for i, landmark in enumerate(self.landmarks):
      annotation_type = annotation_types[i]
      if(i in self.possible_duplicates): 
        link = Link(landmark, True, annotation_type = annotation_type)
      else:
        link = Link(landmark, False, annotation_type = annotation_type)
      self.links[landmark] = link

    self.links["Root"].add_parent(None)

    for limb in limbs:
      parent = self.links[limb]
      for i in limbs[limb]:
        self.links[self.landmarks[i]].add_parent(parent)
        self.links[parent.get_type()].add_child(self.links[self.landmarks[i]])

  def get_root(self):
    return self.links["Root"]
  
  


  def traverse(self):
      next = self.links["Root"]
      while(next is not None):
        
        next, _ = next.successor()
        

class Final_Annotation():

  def __init__(self):
    self.annotations = {"id":[],"pid":[], "type": [], "x":[], "y": [], "x1" : [], "y1": [], "attr":[], "person":[], "img_id":[], "hidden":[], "annotation_type" : []}
    self.next_id = 0
    self.roots = []

  def append(self,annot):
    for col in self.annotations:
      self.annotations[col] = self.annotations[col] + annot.tree[col]
    self.next_id += annot.count
    self.roots = self.roots + annot.roots
    return(self.next_id)

class Annotation_GUI:

    def __init__(self, landmarks, limbs, possible_duplicates, annotation_types, person_id = -1, img_id = 'I-1'):
        self.tree = {"id":[],"pid":[], "type": [], "x":[], "y": [], "x1" : [], "y1": [], "attr":[], "person":[], "img_id":[], "hidden":[], "annotation_type" : [], "children" : []}
        self.count = 0
        self.landmarks = landmarks
        self.img_id = img_id
        self.limbs = limbs
        self.possible_duplicates = possible_duplicates
        self.annotation_types = annotation_types
        self.chain = None
        self.roots = []
        self.current_root = None
        self.current_id = None
        self.person_id = person_id
        
        self.next_link = None
        self.parent_link = None
        self.current_parent = None
        self.img = None


        self.pane = np.zeros((256,256, 3), np.uint8)
        self.temp_pane = None
        self.menu = None
        
        self.temp_entry = {} 
        self.over = False
        self.state = 'main'



#get/set state variable
    def get_state(self):
        return(self.state)
  
    def set_state(self, state):
        self.state = state


  

#find successor link a well as id from a position after selection. If up, find next successor before selection
   
    def successor(self, up = False):


        if(self.next_link.next_child < len(self.next_link.children)):

              tmp = self.next_link.next_child
              self.parent_link = self.next_link 
              self.current_parent = self.current_id
              self.next_link = self.next_link.children[tmp]


        else:
                self.next_link.next_child = 0
                self.next_link = self.parent_link
                self.current_id = self.current_parent

                self.current_parent = self.tree['pid'][self.current_id]
                self.parent_link = self.next_link.parent

                self.successor()


        

    
#Initialising functions
    def add_root(self, attr = ''):

        id = self.count
        self.tree['id'].append(id)
        self.tree['pid'].append(-1)
        self.tree['type'].append("Root")
        self.tree['x'].append(0)
        self.tree['y'].append(0)
        self.tree['x1'].append(-1)
        self.tree['y1'].append(-1)
        self.tree['attr'].append(attr)
        self.tree['person'].append(self.person_id)
        self.tree['img_id'].append(self.img_id)
        self.tree['hidden'].append(True)
        self.tree['children'].append([])
        self.tree['annotation_type'].append("Point")
 
        self.current_id = id
        self.count += 1
        self.state = 'select'
        self.current_parent = id
        self.parent_link = self.chain.get_root()
        self.next_link = self.parent_link

        return(id)

    def start_annotation(self, attr = ''):
        if(self.state != 'main'):
          return(-1)

        self.chain = Chain(self.landmarks, self.limbs, self.possible_duplicates, self.annotation_types)
        self.current_id = self.add_root(attr = attr)
        self.current_root = self.current_id
        self.current_parent = self.current_id
        self.roots.append(self.current_id)
        self.successor()
        return(0)

#Entry functions

    def capture(self, x,y):
        if(self.state == 'select'):

          l_type = self.next_link.get_type()
          self.temp_add(l_type, x, y, self.next_link.get_annotation_type(),'')
          if(self.next_link.get_annotation_type() == "Point"):
              self.state = "confirm"
          elif(self.next_link.get_annotation_type() == "Bbox"):
              self.state = "draw_bbox"

        elif(self.state == 'draw_bbox'):
          self.temp_add2(x, y)
          self.state = 'confirm'
  
    def temp_add(self, l_type, x, y, annot_type, attr = ''):
        self.temp_entry["type"] = l_type
        self.temp_entry["annotation_type"] = annot_type
        self.temp_entry['x'] = x
        self.temp_entry['y'] = y
        self.temp_entry['x1'] = -1
        self.temp_entry['y1'] = -1
        self.temp_entry['attr'] = attr

    def temp_add2(self, x, y): 
        self.temp_entry['x1'] = x
        self.temp_entry['y1'] = y



    def add_entry(self, hidden):
        if(self.state == 'main'):
            return

        idx = self.count
        self.tree['id'].append(idx)
        self.tree['pid'].append(self.current_parent)
        self.tree['type'].append(self.temp_entry["type"])
        self.tree['x'].append(self.temp_entry['x'])
        self.tree['y'].append(self.temp_entry['y'])
        self.tree['x1'].append(self.temp_entry['x1'])
        self.tree['y1'].append(self.temp_entry['y1'])
        self.tree['annotation_type'].append(self.temp_entry['annotation_type'])
        self.tree['attr'].append(self.temp_entry['attr'])
        self.tree['person'].append(self.person_id)
        self.tree['img_id'].append(self.img_id)
        self.tree['hidden'].append(hidden)
        self.tree['children'].append([])
        self.tree['children'][self.current_parent].append(idx)
        
        self.current_id = idx
        print(self.tree['type'][self.current_id] + " Added with id {}".format(self.current_id))

        self.count += 1
        
        self.next_link.touched = True
        if(self.next_link.duplicate_possible):
                pass

        else:
                self.parent_link.next_child += 1
        

        return(idx)




    #Logic for Annotation Progression
    def do_confirm(self, i):
        
        
        if(self.state != 'confirm'):
            return(-1)

        if(self.next_link.get_type() == 'Root'):
            self.successor()
            self.state = 'select'

        if(i == 0):
            self.add_entry(False)
        else:
            self.add_entry(True)
                       
        self.successor()
        self.temp_entry = {}
        self.state = 'select'
    

      
        if(self.next_link.get_type() == 'Root'):
            return(-1)

      
        if(self.next_link.touched):
            return(1)
      

    
    def dont_confirm(self):
        if(self.state != 'confirm'):
            return

    
        self.temp_entry = {}
        self.state = 'select'
        if(self.next_link.touched):
            return(1)
    
  

    def do_select(self, x, y):
        if(self.state == 'select') or (self.state == 'draw_bbox'):
            self.capture(x,y)
 

#Logic for jumping children etc
    def next_child(self):
    
      
      out = self.successor(up = True)
      if(self.next_link.get_type() == 'Root'):
        return(-1)
      
      
      self.state = 'select'
      
      
        
    def set_child(self, id):
        
        if(self.state == 'main'):
            return
        if(id <= self.parent_link.next_child):
            pass
        else:
            self.parent_link.next_child = id
        self.go_up()
    
    def get_child(self):
        
        return self.parent_link.next_child
    
    def go_up(self):
          if (self.state == 'main'):
                return
          
          self.next_link.next_child = 0
          self.next_link = self.parent_link
          if(self.next_link.get_type() == "Root"):
            return (-1)
          
          self.current_parent = self.tree['pid'][self.current_id]
          self.parent_link = self.next_link.parent
          
          
          self.successor()
          self.state = 'select'
          
        
    def traverse(self, idx, last_only = False):
            cx = []
            cy = []
            cz = []
            cx1 = []
            cy1 = []
            cz1 = []
            ax = []
            ay = []
            az = []
            ax1 = []
            ay1 = []
            az1 = []
            children = self.tree['children'][idx]
            cx.append(self.tree['x'][idx])
            cy.append(self.tree['y'][idx])
            cz.append(self.tree['hidden'][idx])
            cx1.append(self.tree['x1'][idx])
            cy1.append(self.tree['y1'][idx])
            cz1.append(self.tree['annotation_type'][idx])
            for i in children:
                ax, ay, ax1, ay1, az, az1 = self.traverse(i)
                if(not last_only):
                    cx = cx + ax
                    cy = cy + ay
                    cz = cz + az
                    cx1 = cx1 + ax1
                    cy1 = cy1 + ay1
                    cz1 = cz1 + az1
                    
                    
            if(last_only):
                cx = cx + ax
                cy = cy + ay
                cz = cz + az
                cx1 = cx1 + ax1
                cy1 = cy1 + ay1
                cz1 = cz1 + az1
            
            return(cx,cy, cx1, cy1, cz, cz1)
            
