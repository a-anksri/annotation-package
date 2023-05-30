import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os



landmarks = ["Root", "Forehead", "Left Eye", "Left Ear", "Left Shoulder", "Left Hip", "Right Eye", "Right Ear", "Right Shoulder", "Right Hip", "Nose", "Left Elbow", "Left Knee", "Right Elbow", "Right Knee", "Left Wrist", "Left Ankle", "Right Wrist", "Right Ankle", "Mouth"]
limbs = {"Root":[1], "Forehead":[10,19,2,6,3,7,4,8,5,9], "Left Shoulder":[11], "Left Elbow": [15], "Left Hip":[12], "Left Knee": [16], "Right Shoulder":[13], "Right Elbow": [17], "Right Hip":[14], "Right Knee": [18]}
possible_duplicates = [1,11,12,13,14]

class Link:

  def __init__(self, landmark, possible = False):
    self.landmark_type = landmark
    self.parent = self
    self.children = []
    self.next_child = 0
    self.duplicate_possible = possible
    self.touched = False
  
  def add_parent(self, parent):
    self.parent = parent

  def add_child(self, child):
    self.children.append(child)

  def get_type(self):
    return self.landmark_type

  def get_parent(self):
    return self.parent

  def check_over(self):
    if(self.next_child == len(self.children)):
      
      return(True)
    else:
      return(False)
  
  

class Chain:

  def __init__(self, landmarks, limbs, possible_duplicates):
    self.landmarks = landmarks
    self.limbs = limbs
    self.possible_duplicates = possible_duplicates
    self.links = {}
    for i, landmark in enumerate(self.landmarks):
      if(i in self.possible_duplicates):
        link = Link(landmark, True)
      else:
        link = Link(landmark, False)
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
    self.annotations = {"id":[],"pid":[], "type": [], "x":[], "y": [], "attr":[], "person":[], "img_id":[], "hidden":[]}
    self.next_id = 0
    self.roots = []

  def append(self,annot):
    for col in self.annotations:
      self.annotations[col] = self.annotations[col] + annot.tree[col]
    self.next_id += annot.count
    self.roots = self.roots + annot.roots
    return(self.next_id)

class Annotation_GUI:

    def __init__(self, landmarks, limbs, possible_duplicates, person_id = -1, img_id = 'I-1'):
        self.tree = {"id":[],"pid":[], "type": [], "x":[], "y": [], "attr":[], "person":[], "img_id":[], "hidden":[], "children":[]}
        self.count = 0
        self.landmarks = landmarks
        self.img_id = img_id
        self.limbs = limbs
        self.possible_duplicates = possible_duplicates
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
        self.menuText = ''
        self.temp_entry = {}
        self.elements = {"yes":[], "no":[]}
        self.over = False

        self.state = 'main'

        self.elements = []


#get/set state variable
    def get_state(self):
        return(self.state)
  
    def set_state(self, state):
        self.state = state


  

#find successor link a well as id from a position after selection. If up, find next successor before selection
    def predecessor(self):
        pass
        
    
    def successor(self, up = False):

        '''       
        if(up):
            if(self.next_link.duplicate_possible):
                self.parent_link.next_child += 1
            else:
                pass

              self.next_link = self.parent_link
              if(self.next_link.get_type() == "Root"):
                return (-1)

              self.current_parent = self.tree['pid'][self.current_id]
              self.parent_link = self.next_link.parent


              self.successor()
              print("At exit. up = true")
              print(self.current_id, self.current_parent, self.next_link.get_type(), self.next_link.next_child, self.parent_link.get_type(), self.parent_link.next_child)
              return
        '''

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
        self.tree['attr'].append(attr)
        self.tree['person'].append(self.person_id)
        self.tree['img_id'].append(self.img_id)
        self.tree['hidden'].append(True)
        self.tree['children'].append([])
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

        self.chain = Chain(landmarks, limbs, possible_duplicates)
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
          self.temp_add(l_type, x, y, '')
          #self.draw_point_on_pane(x,y)
  
    def temp_add(self, l_type, x, y, attr = ''):
        self.temp_entry["type"] = l_type
        self.temp_entry['x'] = x
        self.temp_entry['y'] = y
        self.temp_entry['attr'] = attr



    def add_entry(self, hidden):
        if(self.state == 'main'):
            return

        idx = self.count
        self.tree['id'].append(idx)
        self.tree['pid'].append(self.current_parent)
        self.tree['type'].append(self.temp_entry["type"])
        self.tree['x'].append(self.temp_entry['x'])
        self.tree['y'].append(self.temp_entry['y'])
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
        
        if(self.state == 'main'):
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
        if(self.state == 'main'):
            return

    
        self.temp_entry = {}
        self.state = 'select'
        if(self.next_link.touched):
            return(1)
        
      #self.refresh_pane(self.current_id)
    
    
    
    

    

    def do_select(self, x, y):
        if(self.state == 'select'):
          self.capture(x,y)

          self.state = 'confirm' 
          #self.draw_confirmation(x,y)   

    

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
          

    def delete_previous(self):
        if(status == 'main'):
            return
        
        self.predecessor()
        #self.tree = self.tree
        
    def traverse(self, idx, last_only = False):
            cx = []
            cy = []
            cz = []
            ax = []
            ay = []
            az = []
            children = self.tree['children'][idx]
            cx.append(self.tree['x'][idx])
            cy.append(self.tree['y'][idx])
            cz.append(self.tree['hidden'][idx])
            for i in children:
                ax, ay, az = self.traverse(i)
                if(not last_only):
                    cx = cx + ax
                    cy = cy + ay
                    cz = cz + az
                    
                    
            if(last_only):
                cx = cx + ax
                cy = cy + ay
                cz = cz + az
            
            return(cx,cy,cz)
            
            

            
        

class Element:
    
    def __init__(self,text, duplicate, offset, dim, default = 0):
        self. x_offset = offset[0]
        self.y_offset = offset[1]
        self.color1 = [(0,255,0),(255,0,0),(0,255,255),(0,0,0)]
        self.color2 = [(0,0,0),(255,255,255),(0,0,0),(255,255,255)]
        self.default = default
        self.dim = dim
        self.text = text
        self.state = 0
        self.duplicate = duplicate
        
        
    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def has(self,x,y, menu_offset):
        if((x > menu_offset[0] + self.x_offset) and (x < menu_offset[0] + self.x_offset + self.dim[0]) and (y > menu_offset[1] + self.y_offset) and (y < menu_offset[1] + self.y_offset + self.dim[1])):
           return (True)
        return (False)
    
    #Functions to add more colors
    def set_back_color(self,color1, color2):
        self.color1.append(color1)
        self.color2.append(color2)
        return(len(self.color1) - 1)
        
        

class Gui:
    
    def __init__(self, window_size = (1028,700)):
        
        #Content for display
        self.image = None
        self.canvas = None
        self.scaled_canvas = None
        self.msg1 = None
        self.msg2 = None
        self.tmpmsg1 = None
        self.tmpmsg2 = None
        
        
        #Child links to be displayed on the screen
        self.elements = []
        
        #Buttons for zoom/pan
        self.image_controls = []
        self.cx = []
        self.cy = []
        self.cz = []
        self.current_link = None
        
        #Buttons of confirmation dialog box
        self.buttons = []
        
        #image positioning variables
        
        #Position of image in window
        self.imx1 = 0
        self.imy1 = 0
        self.imx2 = 0
        self.imy2 = 0
        
        #Scale from original image
        self.scale = 1.0
        
        #x and y shifts (considered after scaling)
        self.x_pan = 0
        self.y_pan = 0
        self.lazy = True
        
        
        #Used for mouse drag based panning
        self.stablex_pan = 0
        self.stabley_pan = 0
        self.current_selx = 0
        self.current_sely = 0
        
        #Whether confirmation dialog box is to be displayed
        self.dialog_on = False
        
        
        #nth child element is to be highlighted
        self.num = 0
        
        #Offset and sizes of various panes
        
        
        self.window_size = window_size
        message_strip_height = 130
        menu_strip_width = 128
        self.image_offset = (5,5)
        self.message_offset = (0,window_size[1]- message_strip_height)
        self.menu_offset = (window_size[0] - menu_strip_width,0)
        self.message_size = (window_size[0] - menu_strip_width,message_strip_height)
        self.menu_size = (menu_strip_width,window_size[1])
        self.image_size = (window_size[0] - menu_strip_width,window_size[1] - message_strip_height)
        self.dialog_offset = (0,0)
        self.dialog_size = (300,150)
        
        
        
        #Making blank panes for each component
        self.base = np.zeros((self.window_size[1],self.window_size[0],3), np.uint8)
        self.message_pane_base = np.zeros((self.message_size[1],self.message_size[0],3), np.uint8)
        self.message_pane_base[:,:,1] = np.ones((self.message_size[1],self.message_size[0]), np.uint8) * 64
        self.message_pane_base[:,:,2] = np.ones((self.message_size[1],self.message_size[0]), np.uint8) * 140
        self.menu_pane_base = np.zeros((self.menu_size[1],self.menu_size[0],3), np.uint8)
        self.menu_pane_base[:,:,1] = np.ones((self.menu_size[1],self.menu_size[0]), np.uint8)
        self.menu_pane_base[:,:,2] = np.ones((self.menu_size[1],self.menu_size[0]), np.uint8) * 128
        self.image_pane_base = np.zeros((self.image_size[1],self.image_size[0],3), np.uint8)
        self.dialog_base = np.ones((self.dialog_size[1],self.dialog_size[0],3), np.uint8) * 150
        
        self.window = self.base.copy()
        self.image_pane = self.image_pane_base.copy()
        self.menu_pane = self.menu_pane_base.copy()
        self.message_pane = self.message_pane_base.copy()
        self.dialog_pane = self.dialog_base.copy()
        
    #Show dialog box for confirmation of selection  
    def add_dialog(self,x,y, typ = 0):
        
        if(typ == 0):
            #Hard coded button sizes and placement in dialog box
            self.buttons.append(Element("Visible", False,(10,110), (70,30), default = 0))
            self.buttons.append(Element("Hidden", False,(110,110), (70,30), default = 1))
            self.buttons.append(Element("Cancel", False,(210,110), (70,30), default = 2))
                            
        for i in self.buttons:
                self.add_to_pane(i)
        self.dialog_on = True
        
        #Setting location of dialog box just below the cursor
        xmin = max(x-100,0)
        xmin = min(xmin,self.window_size[0],self.window_size[0] - 350) 
        if ((y + 150) > self.message_offset[1]):
            ymax = y - 200
        else:
            ymax = y + 50
        self.dialog_offset = (xmin,ymax)
        self.dialog_pane = cv.putText(self.dialog_pane, "Confirm or Cancel", (40,40), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = 0.7, color = (0,0,0), thickness = 2)
        
    
    #utility function to add buttons to dialog pane       
    def add_to_pane(self, element):
        
        x_offset = element.x_offset
        y_offset = element.y_offset
        back_color = element.color1[element.default]
        font_color = element.color2[element.default]
        x_dim = element.dim[0]
        y_dim = element.dim[1]
        
        cv.rectangle(self.dialog_pane, (x_offset, y_offset), (x_offset + x_dim, y_offset+y_dim), color = back_color, thickness = -1)
        self.dialog_pane = cv.putText(self.dialog_pane, element.text, (x_offset + 10,y_offset + 20), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = 0.45, color = font_color, thickness = 2)
        
    #To show an alert message in message pane. Can revert to prior normal message after reset_alert
    def alert(self, text1 = "Alert!", text2 = "", old = False):
        
        self.tmpmsg1 = self.msg1
        self.msg1 = text1
        self.tmpmsg2 = self.msg2
        if(old):
            pass
        else:
            self.msg2 = text2
            
    #To reset message pane back to normal messages
    def reset_alert(self, text, old = False):
        self.msg1 = self.tmpmsg1
        if(old):
            self.msg2 = self.tmpmsg2
        else:  
            self.msg2 = text
            self.tmpmsg1 = None
            self.tmpmsg2 = None
        
        
        
    #change messages for message pane
    def add_message(self, msg1 = None, msg2 = None, retain = True):
        if(retain):
            if(msg1 is None):
                pass
            else:
                self.msg1 = msg1
            if(msg2 is None):
                pass
            else:
                self.msg2 = msg2
        
        else:
            if(msg1 is None):
                self.msg1 = ''
            else:
                self.msg1 = msg1
            if(msg2 is None):
                self.msg1 = ''
            else:
                self.msg2 = msg2
    
    #Add elements to menu pane. Skip all is also added
    def add_elements(self, current):
        
        self.current_link = current
        current_children = self.current_link.children
        
        gap = int((self.message_offset[1] - 40)/(len(current_children)+2) - 30)
        offset = gap + 40
        self.elements = []
        self.num = 0
        for i in current_children:
            
            element = Element(i.get_type(), i.duplicate_possible, (10,offset), (90,30))
            offset += gap + 30
            self.elements.append(element)
        
        element = Element("Skip All", False, (10,offset), (90,30), 3)   
        self.elements.append(element)
        self.elements[0].set_state(1)
    
    def reset_elements(self):
        self.elements = []
        
    def reset_dialog(self):
        self.buttons = []
        self.dialog_on = False
        
    #Add image control buttons
    def add_image_controls(self):
        end = self.message_offset[1] - 20
        self.image_controls.append(Element('+', False, (20,end + 10),(40,40), default = 2))
        self.image_controls.append(Element('-', False, (80,end + 10),(40,40), default = 2))
        self.image_controls.append(Element('->', False, (90,end + 75),(30,30)))
        self.image_controls.append(Element('<-', False, (0,end + 75),(30,30)))
        self.image_controls.append(Element('up', False, (50,end + 55),(30,30)))
        self.image_controls.append(Element('do', False, (50,end + 95),(30,30)))
    
    def add_image(self, img):
        self.image = img
        self.canvas = self.image.copy()
        
        width = img.shape[1]
        height = img.shape[0]
        
        sc_x = self.image_size[0]/width
        sc_y = self.image_size[1]/height
        self.scale = min(sc_x, sc_y)
    
    #To flush all temporary marks and redraw the canvas
    def flush_canvas(self):
        self.canvas = self.image.copy()
    
    #Compose the image pane
    def compose_image(self, pre = False):
        scale = self.scale
        x_pan = self.x_pan
        y_pan = self.y_pan
        x_pos = 0
        y_pos = 0
        self.flush_canvas()
        cp = self.canvas.copy()
        if(not self.lazy):
            for i, lis in enumerate(zip(self.cx, self.cy, self.cz)):
                x,y,z = lis
                if(i == 0):
                    self.paint(x,y, z, typ = 0)
                else:
                    self.paint(x,y, z, typ = 2)
            
        
        width = cp.shape[1]
        height = cp.shape[0]
        
        sc_width = int(scale * width)
        sc_height = int(scale * height)
        self.x_pan = min(self.x_pan, sc_width - self.image_size[0])
        self.y_pan = min(self.y_pan, sc_height - self.image_size[1])
        
        if(sc_width <= self.image_size[0]):
            x_pan = 0
            self.x_pan = 0
            x_pos = int((self.image_size[0] - sc_width)/2)
        
        if(sc_height <= self.image_size[1]):
            y_pan = 0
            self.y_pan = 0
            y_pos = int((self.image_size[1] - sc_height)/2)
        
        
        
        self.scaled_canvas = cv.resize(cp, (sc_width, sc_height))
        if(self.lazy):
            for i, lis in enumerate(zip(self.cx, self.cy, self.cz)):
                x,y,z = lis
                if(i == 0):
                    self.paint(x,y, z, typ = 0)
                else:
                    self.paint(x,y, z, typ = 2)
        
        self.draw_selection()
        im_width = int(min(sc_width, self.image_size[0]))
        im_height = int(min(sc_height, self.image_size[1]))
        cp = self.scaled_canvas[self.y_pan:self.y_pan + im_height, self.x_pan:self.x_pan + im_width,:]
        
            
        
        
        self.image_pane[y_pos:y_pos+im_height, x_pos: x_pos + im_width,:] = cp
        self.imx1 = x_pos
        self.imx2 = x_pos+im_width
        self.imy1 = y_pos
        self.imy2 = y_pos +im_height
        
        
        
        
    def get_current_element(self):
        return(self.num, self.elements[self.num].duplicate)
    
    #Setting current element based on user selection. Corresponding changes should be made in annotation class too
    def set_current_element(self, num):
        
        if(num <= self.num):
            return(-1)
        if(num > len(self.elements)):
            return(-1)
        
            
        for i in range(num):
            self.elements[i].set_state(2)
        
        self.elements[num].set_state(1)
        self.num = num
    
    #To convert pixel values from image pane to original image
    def rescale_coords(self,x,y):
        x = x - self.imx1 + self.x_pan
        y = y - self.imy1 + self.y_pan
        x = int(x/self.scale)
        y = int(y/self.scale)
        return(x,y)
    
    #To return landmark coordinates into image pane coords
    def unscale_coords(self, x, y):
        x = int(x * self.scale)
        y = int(y* self.scale)
        
        return(x,y)
    
    def draw_selection(self):
        if(self.dialog_on):
            x, y = self.unscale_coords(self.current_selx, self.current_sely)
            self.draw_circle(self.scaled_canvas, x, y, 4)
        
    
    def draw_circle(self, pane, x,y, typ = 0):
        if(typ == 0):
            cv.circle(pane, (x,y), 3, (0,255,0), -1)
            cv.circle(pane, (x,y), 6, (0,255,0), 2)
            cv.circle(pane, (x,y), 8, (0,255,0), 1)
        elif(typ == 1):
            cv.circle(pane, (x,y), 3, (0,255,255), -1)
            cv.circle(pane, (x,y), 6, (0,255,0), 2)
            
            cv.circle(pane, (x,y), 8, (0,255,0), 1)
        elif(typ == 2):
            cv.circle(pane, (x,y), 3, (0,128,255), 2)
        elif(typ == 3):
            cv.circle(pane, (x,y), 3, (0,128,255), 2)
        elif(typ == 4):
            cv.circle(pane, (x,y), 3, (255,0,0), 2)
            
    def draw_line(self, x1, y1, x2, y2):
        cv.line(self.canvas, (x1,y1), (x2, y2), (255,255,255), 2)
        
    #Used for dragging based panning        
    def pan(self,x,y):
        
        
        inc = int(min(x, self.image.shape[1] * self.scale - self.stablex_pan - self.image_size[0]))
        inc = max(inc,-1*self.stablex_pan)
        
        self.x_pan = self.stablex_pan + inc
        
        inc = int(min(y, self.image.shape[0] * self.scale - self.stabley_pan - self.image_size[1]))
        inc = max(inc,-1*self.stabley_pan)
        self.y_pan = self.stabley_pan + inc
        
    def reset_pan(self):
        self.stablex_pan = self.x_pan
        self.stabley_pan = self.y_pan
    
    #Used to set position of image in the image pane whenever image control buttons used
    def image_position(self, num):
        if(num == 0):
            self.scale = min(2,self.scale * 1.1)
        elif (num == 1):
            if(self.image.shape[1] * self.scale < self.image_size[0]) and (self.image.shape[0] * self.scale < self.image_size[1]):
                pass
            else:
                self.scale = self.scale / 1.1
        elif (num == 2):
            inc = int(min(50, self.image.shape[1] * self.scale - self.x_pan - self.image_size[0]))
            inc = max(0, inc)
            self.x_pan += inc
        elif (num == 3):
            inc = min(50, self.x_pan)
            self.x_pan -= inc
        elif (num == 4):
            inc = min(50, self.y_pan)
            self.y_pan -= inc
        elif (num == 5):
            inc = int(min(50, self.image.shape[0] * self.scale - self.y_pan - self.image_size[1]))
            inc = max(0, inc)
            self.y_pan += inc
        self.stablex_pan = self.x_pan
        self.stabley_pan = self.y_pan
    
    #To check if a menu element is clicked
    def check_within(self, x, y):
        
        for i, element in enumerate(self.elements):
            if (element.has(x,y, self.menu_offset)):
                return(i)
            
        return(-1)
    
    #To check if an image control button is clicked
    def check_image_controls(self, x, y):
        
        for i, element in enumerate(self.image_controls):
            if (element.has(x,y, self.menu_offset)):
                return(i)
            
        return(-1)
    
    #To paint circles in place of landmarks
    def paint(self, parentx, parenty, hidden, typ = 0):
        
        if(self.lazy):
            pane = self.scaled_canvas
            parentx, parenty = self.unscale_coords(parentx, parenty)
        else:
            pane = self.canvas
                
        
        t = typ
        if(hidden):
            self.draw_circle(pane,parentx, parenty, typ = t+1)
        else:
            self.draw_circle(pane, parentx, parenty, typ = t)
        
        
     #To check if dialog box buttons are clicked    
    def check_within_buttons(self, x, y):
        
        for i, element in enumerate(self.buttons):
            if (element.has(x,y, self.dialog_offset)):
                return(i)
            
        return(-1)
     
    #To check if a point within current image borders is clicked
    def check_within_image(self, x, y):
        
        if((x > self.imx1) and (x < self.imx2) and (y > self.imy1) and (y < self.imy2)):
           return (True)
        return (False)
        
            
        return(-1)
    
    
     #Compose message pane                           
    def compose_message(self):
        l1 = len(self.msg1)
        l2 = len(self.msg2)
        if(l1 <= 52):
                l1scale = 1
        else:
                l1scale = 51.0/l1
        
        if(l2 <= 65):
                l2scale = 0.8
        else:
                l2scale = 52.0/l2
        
        pane = cv.putText(self.message_pane, self.msg1, (20,40), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = l1scale, color =  (0,255,255), thickness = 2)
        self.message_pane = cv.putText(pane, self.msg2, (20,100), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = l2scale, color =  (0,255,255), thickness = 2)
     
    #compose menu pane
    def compose_menu(self, pre = False):
        
        scale = 1.0
        if(pre):
            self.menu_pane = self.menu_pane_base.copy()
        else:
            name = self.current_link.get_type()
            l = len(name)
            if(l <= 8):
                    scale = 0.75
            else:
                    scale = 6.0/l
            self.menu_pane = cv.putText(self.menu_pane, name, (15, 35), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = scale, color = (0,255,255), thickness = 3  )

            for i in self.elements:

                l = len(i.text)
                if(l <= 12):
                    scale = 0.5
                else:
                    scale = 6.0/l

                color1 = i.color1[i.state]
                color2 = i.color2[i.state]
                init_y = i.y_offset
                init_x = i.x_offset
                self.menu_pane = cv.rectangle(self.menu_pane, (init_x, init_y), (init_x + i.dim[0], init_y + i.dim[1]), color = color1, thickness = -1 )
                self.menu_pane = cv.putText(self.menu_pane, i.text, (init_x+5, init_y + 15), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = scale, color = color2, thickness = 2  )
        
            for i in self.image_controls:

                color1 = (0,255,0)
                color2 = (0,0,0)
                scale = 0.5
                init_y = i.y_offset
                init_x = i.x_offset
                self.menu_pane = cv.rectangle(self.menu_pane, (init_x, init_y), (init_x + i.dim[0], init_y + i.dim[1]), color = color1, thickness = -1 )
                self.menu_pane = cv.putText(self.menu_pane, i.text, (init_x+5, init_y + 15), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = scale, color = color2, thickness = 3  )


     #Compose total window   
    def destroy(self):
        self.msg1 = None
        self.msg2 = None
        self.elements = []
        self.flush_canvas()
        self.cx = []
        self.cy = []
        self.cz = []
        
    
    def compose(self, pre = False):
        
            
        self.compose_message()
        self.compose_menu(pre)
        self.compose_image(pre)
        self.window[self.message_offset[1]:self.message_offset[1] + self.message_size[1], self.message_offset[0]:self.message_offset[0] + self.message_size[0],:] = self.message_pane
        self.window[self.menu_offset[1]:self.menu_offset[1] + self.menu_size[1], self.menu_offset[0]:self.menu_offset[0] + self.menu_size[0],:] = self.menu_pane
        self.window[self.image_offset[1]:self.image_offset[1] + self.image_size[1], self.image_offset[0]:self.image_offset[0] + self.image_size[0],:] = self.image_pane
        
        if(self.dialog_on):
            temp = self.base.copy()
            
           
           
            self.window[self.dialog_offset[1]:self.dialog_offset[1] + self.dialog_size[1], self.dialog_offset[0]:self.dialog_offset[0] + self.dialog_size[0],:] = self.dialog_pane
            
        self.imx1 += self.image_offset[0]
        self.imx2 += self.image_offset[0]
        self.imy1 += self.image_offset[1]
        self.imy2 += self.image_offset[1]
        
        
        
        self.menu_pane = self.menu_pane_base.copy()
        self.message_pane = self.message_pane_base.copy()
        self.image_pane = self.image_pane_base.copy()
        return self.window.copy()
        

def keyboard_input(gui, person_id, name = 'Preliminary View'):
    if(person_id == 0):
        msg = "Start Annotation. Enter Attributes for the first person ('-1' to escape)"
    else:
        msg = "Starting New Person. Enter Attributes (-1 to escape)"
    text = ""
    letters = string.printable
    
    while True:
        if len(text) == 0:
            disp = "__"
        else:
            disp = text
        gui.add_message(msg,disp)
        window = gui.compose(pre = True)
        cv.imshow(name, window)
        key = cv.waitKey(10)
        if(key == 8):
            text = text[:-1]
        if key == ord("\n") or key == ord("\r"): # Enter Key
            break
        for letter in letters:
            if key == ord(letter):
                text = text + letter
        
    cv.destroyWindow(name)  
    return text

drag = False
ix = 0
iy = 0
def dummy_handler(event,x,y,flags, params):
    pass

def handler(event, x, y, flags, params):
    global drag, ix, iy
    
    annot = params[0]
    gui = params[1]
    text = params[2]
    state = annot.get_state()
    
    if(event == cv.EVENT_RBUTTONUP):
        out = gui.check_within_image(x,y)
        if(drag):
            drag = False
            ix = 0
            iy = 0
            gui.reset_pan()
            gui.reset_alert("Pan Mode Off")
            
            return
        
        
        drag = True
        ix = x
        iy = y
        
        
        gui.alert("Pan mode On, Right Click Again to Deactivate", "", old = False)
                
        
        
        
    if(event == cv.EVENT_MOUSEMOVE):
        
        if(drag):
            out = gui.check_within_image(x,y)
            if(out):
                
                gui.pan(ix - x, iy - y)
                
    
    
    
    
    
    if(event == cv.EVENT_LBUTTONUP):
        
        if(drag):
            
            return
        
        if(gui.dialog_on):
            num = gui.check_within_buttons(x,y)
            if(num > -1):
                
                if(num == 0):
                    out = annot.do_confirm(num)
                    
                    
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), text)
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), text)
                    gui.reset_dialog()
                    
                    
                    
                    
                elif(num == 1):
                    out = annot.do_confirm(num)
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), "Selection Recorded")
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), "Selection Recorded")
                    gui.reset_dialog()
                    
                    
                else:
                    out = annot.dont_confirm()
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), "Selection Cancelled")
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), "Cancelled")
                    gui.reset_dialog()
                    
                gui.flush_canvas()
                  
                gui.add_elements(annot.parent_link)
                    
            return
        
        
        
        gui.flush_canvas()
        num = gui.check_within(x,y)
        if num > -1:
            
            
            annot.set_child(num)
            
            if(annot.next_link.get_type() == "Root"):
                    gui.add_message("Annotation Complete" "ANN")
                    
                    return
            
    
            gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), "")
            gui.add_elements(annot.parent_link)
            
        
        
        num = gui.check_image_controls(x,y)
        if (num > -1):
            gui.image_position(num)
            
        out = gui.check_within_image(x,y)
        x1,y1 = gui.rescale_coords(x,y)
        
        if(out):
            gui.current_selx, gui.current_sely = x1, y1
            
            gui.add_dialog(x,y)
            annot.do_select(x1,y1)
            
            
        
            
        
        
def tool_GUI(img_name, All_annotations, name = 'View', img = None, window_size = (1028,768), next_id = 0):
  
  gui = Gui(window_size)
  person_id = next_id
  added = False
  added_count = 0
  
  
  gui.add_image(img)
  gui.add_image_controls()
  
  
  
  
  while(True):
    
    annot = Annotation_GUI(landmarks, limbs, possible_duplicates, person_id = person_id, img_id = img_name)
    
    
    attr = keyboard_input(gui, person_id, name = name)
    if(attr == '-1'):
        break
        
    annot.start_annotation(attr)
    
    cv.namedWindow(name)
    cv.setMouseCallback(name, handler, (annot,gui, attr) )
    gui.add_elements(annot.parent_link)
    gui.set_current_element(0)
    gui.add_message("Select a Forehead", attr)

    annot.set_state('select')
    gui.flush_canvas()
    more = False
    complete = False
    to_save = True
    alert = False

    
    
    while(True):

        
        
        num = annot.get_child()
        
        
        gui.set_current_element(num)
        if(annot.next_link.get_type() == 'Root'):
            gui.add_message("Annotation Complete","Press 'a' to save and add person, Press 's' to save and quit, 'q' to quit without saving")
            annot.set_state('main')
            cv.setMouseCallback(name, dummy_handler, (annot,gui) )
            complete = True
        
        gui.cx, gui.cy, gui.cz = annot.traverse(annot.current_parent)
        window = gui.compose()
            
        
        cv.imshow(name, window)
        
            
        a = cv.waitKey(20)
        
        if(annot.get_state() == 'confirm' and a == ord(' ')):
            out = annot.do_confirm(0)
            gui.reset_dialog()
            
            if(out == 1):
                    gui.add_message("Select another " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            else:
                    gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            gui.reset_dialog()
            
            gui.flush_canvas()
                  
            gui.add_elements(annot.parent_link)
        
        if(annot.get_state() == 'confirm' and a == ord('h')):
            out = annot.do_confirm(1)
            gui.reset_dialog
                    
                    
            if(out == 1):
                    gui.add_message("Select another " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            else:
                    gui.add_message("Select a " + annot.next_link.get_type() + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            gui.reset_dialog()
            
            gui.flush_canvas()
                  
            gui.add_elements(annot.parent_link)
            
        if (a == ord('q') and complete):
            to_save = False
            break
        
        if (a == ord('q') and not complete):
            gui.add_message("Annotation is incomplete", "'a': Save and add person, 's': Save and Quit, 'x' Quit without saving, 'n': add person without saving")
            alert = True
            
        elif(a == ord('a')):
            to_save = True
            more = True
            added_count += 1
            break
        
        elif(a == ord('s')):
            to_save = True
            more = False
            added_count += 1
  
            break
        
        elif(a == ord('x') and alert):
            to_save = False
            more = False
            break
            
        elif(a == ord('n') and alert):
            to_save = False
            more = True
            break
            
        
            
        
      
        
    
    if(to_save):
      next_id = All_annotations.append(annot)
      added = True
      
    cv.destroyAllWindows()
    
    

    if(not more):
      break
    if(to_save):
        person_id += 1
        gui.destroy()

  cv.destroyAllWindows()
  if(added_count > 0):
      added = True
  return (added)