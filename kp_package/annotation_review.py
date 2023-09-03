import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os

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

class Point:
    
    def __init__(self, id, pid, x, y, x1, y1, typ, hidden, annot_type, attr):
        self.id = id
        self.pid = pid
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1
        self.typ = typ
        self.hidden = hidden
        self.annot_type = annot_type
        self.attr = attr
        self.parent_x = 0
        self.parent_y = 0
        self.p_is_forehead = False
        self.is_forehead = False

    def update_parent_coords(self, x, y):
        self.parent_x = x
        self.parent_y = y

    def has(self, x,y, offset):
      true_x = x
      true_y = y
      
      if(self.x - true_x > -9) and (self.x - true_x < 9) and (self.y - true_y > -9) and (self.y - true_y < 9) and (self.annot_type == 'Point'):
          return(True)
      elif((self.x - true_x) * (self.x1 - true_x) < 0) and ((self.y - true_y) * (self.y1 - true_y) < 0) and (self.annot_type == 'Bbox'):
          return(True)
      else:
        return(False)


        
        

class Display_GUI:
    def __init__(self, window_size = (1028,700)):
        
        #Content for display
        self.image = None
        self.canvas = None
        self.scaled_canvas = None
        self.msg1 = ''
        self.msg2 = ''
        self.tmpmsg1 = ''
        self.tmpmsg2 = ''
        
        #Buttons for zoom/pan
        self.image_controls = []
        self.points = []
        self.show_annotations = True
        self.show_limb = True
        
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
        self.is_alert = False
        
        
        #Used for mouse drag based panning
        self.stablex_pan = 0
        self.stabley_pan = 0
        self.current_selx = 0
        self.current_sely = 0
        
        
        
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
        
        #Making blank panes for each component
        self.base = np.zeros((self.window_size[1],self.window_size[0],3), np.uint8)
        self.message_pane_base = np.zeros((self.message_size[1],self.message_size[0],3), np.uint8)
        self.message_pane_base[:,:,1] = np.ones((self.message_size[1],self.message_size[0]), np.uint8) * 64
        self.message_pane_base[:,:,2] = np.ones((self.message_size[1],self.message_size[0]), np.uint8) * 140
        self.menu_pane_base = np.zeros((self.menu_size[1],self.menu_size[0],3), np.uint8)
        self.menu_pane_base[:,:,1] = np.ones((self.menu_size[1],self.menu_size[0]), np.uint8)
        self.menu_pane_base[:,:,2] = np.ones((self.menu_size[1],self.menu_size[0]), np.uint8) * 128
        self.image_pane_base = np.zeros((self.image_size[1],self.image_size[0],3), np.uint8)
        
        
        self.window = self.base.copy()
        self.image_pane = self.image_pane_base.copy()
        self.menu_pane = self.menu_pane_base.copy()
        self.message_pane = self.message_pane_base.copy()
        
        
    
    #To show an alert message in message pane. Can revert to prior normal message after reset_alert
    def alert(self, text1 = "Alert!", text2 = "", old = False):
        if(not self.is_alert):
            self.tmpmsg1 = self.msg1
            self.tmpmsg2 = self.msg2
        self.is_alert = True
        self.msg1 = text1
        if(old):
            pass
        else:
            self.msg2 = text2
        
            
    #To reset message pane back to normal messages
    def reset_alert(self, text = '', old = False):
        if(not self.is_alert):
            return

        self.msg1 = self.tmpmsg1
        if(old):
            self.msg2 = self.tmpmsg2
        else:  
            self.msg2 = text
            self.tmpmsg1 = ''
            self.tmpmsg2 = ''
        self.is_alert = False
        
        
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
    
    def add_point(self, point):
      self.points.append(point)

    #To flush all temporary marks and redraw the canvas
    def flush_canvas(self):
        self.canvas = self.image.copy()
    
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

    def draw_line(self, pane, x1, y1, x2, y2):
        cv.line(pane, (x1,y1), (x2, y2), (255,255,255), 2)

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
            cv.circle(pane, (x,y), 3, (0,255,255), -1)
            cv.circle(pane, (x,y), 6, (0,255,0), 2)
        elif(typ == 4):
            cv.circle(pane, (x,y), 3, (255,0,0), 2)
    
    def toggle_annotations(self):
        self.show_annotations = not self.show_annotations
    
    def toggle_limb(self):
        self.show_limb = not self.show_limb
    
    def draw_canvas(self):
      pass

    def draw_scaled_canvas(self):
      
      if(not self.show_annotations):
            return
        
      #Drawing points
      for point in self.points:
          
        scaled_x,scaled_y = self.unscale_coords(point.x, point.y)
        scaled_x1,scaled_y1 = self.unscale_coords(point.x1, point.y1)
        if(point.annot_type == 'Bbox'):
            self.paint_bbox(self.scaled_canvas, scaled_x,scaled_y,scaled_x1,scaled_y1)
        else:
          if(point.hidden == True):
              self.draw_circle(self.scaled_canvas,scaled_x,scaled_y,typ = 1)
          else:
              self.draw_circle(self.scaled_canvas,scaled_x,scaled_y,typ = 3)

      #Draw limbs
        if(point.p_is_forehead) or (point.is_forehead) or (point.annot_type == 'Bbox'):
          pass
        else:
          if(self.show_limb):
            scaled_px,scaled_py = self.unscale_coords(point.parent_x, point.parent_y)
            self.draw_line(self.scaled_canvas, scaled_x, scaled_y, scaled_px, scaled_py)


    def paint_bbox(self, pane, x, y, x1, y1):


        cv.rectangle(pane, (x,y), (x1, y1), (0,255,255), 2)    


    #Compose the image pane
    def compose_image(self, pre = False):
        scale = self.scale
        x_pan = self.x_pan
        y_pan = self.y_pan
        x_pos = 0
        y_pos = 0
        self.flush_canvas()
        cp = self.canvas
        self.draw_canvas()
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
        
        
        
        self.scaled_canvas = cv.resize(self.canvas, (sc_width, sc_height))
        self.draw_scaled_canvas()
        
        im_width = int(min(sc_width, self.image_size[0]))
        im_height = int(min(sc_height, self.image_size[1]))
        cp = self.scaled_canvas[self.y_pan:self.y_pan + im_height, self.x_pan:self.x_pan + im_width,:]
        
        self.image_pane[y_pos:y_pos+im_height, x_pos: x_pos + im_width,:] = cp
        self.imx1 = x_pos
        self.imx2 = x_pos+im_width
        self.imy1 = y_pos
        self.imy2 = y_pos +im_height
        
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
            
            for i in self.image_controls:

                color1 = (0,255,0)
                color2 = (0,0,0)
                scale = 0.5
                init_y = i.y_offset
                init_x = i.x_offset
                self.menu_pane = cv.rectangle(self.menu_pane, (init_x, init_y), (init_x + i.dim[0], init_y + i.dim[1]), color = color1, thickness = -1 )
                self.menu_pane = cv.putText(self.menu_pane, i.text, (init_x+5, init_y + 15), fontFace = cv.FONT_HERSHEY_SIMPLEX, fontScale = scale, color = color2, thickness = 3  )

 
    def compose(self, pre = False):
        
            
        self.compose_message()
        self.compose_menu(pre)
        self.compose_image(pre)
        self.window[self.message_offset[1]:self.message_offset[1] + self.message_size[1], self.message_offset[0]:self.message_offset[0] + self.message_size[0],:] = self.message_pane
        self.window[self.menu_offset[1]:self.menu_offset[1] + self.menu_size[1], self.menu_offset[0]:self.menu_offset[0] + self.menu_size[0],:] = self.menu_pane
        self.window[self.image_offset[1]:self.image_offset[1] + self.image_size[1], self.image_offset[0]:self.image_offset[0] + self.image_size[0],:] = self.image_pane
        
         
        self.imx1 += self.image_offset[0]
        self.imx2 += self.image_offset[0]
        self.imy1 += self.image_offset[1]
        self.imy2 += self.image_offset[1]
        
        
        
        self.menu_pane = self.menu_pane_base.copy()
        self.message_pane = self.message_pane_base.copy()
        self.image_pane = self.image_pane_base.copy()
        return self.window.copy()

    #Code for image controls
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
    
    
    
    #To check if an image control button is clicked
    def check_image_controls(self, x, y):
        
        for i, element in enumerate(self.image_controls):
            if (element.has(x,y, self.menu_offset)):
                return(i)
            
        return(-1)
    
    def check_within_image(self, x, y):
        
        if((x > self.imx1) and (x < self.imx2) and (y > self.imy1) and (y < self.imy2)):
           return (True)
        return (False)
        
            
        return(-1)
    
    def check_within_points(self, x, y):
        
        lis = []

        for i, point in enumerate(self.points):
          
          x1, y1 = self.rescale_coords(x,y)
          
          if(point.has(x1,y1, self.image_offset)):
            lis.append(i)
        
        return(lis)
        
        return(-1)

    def get_name(self, lis):
      text = ''
      for id in lis:
            text = text + " " + self.points[id].typ + ", "
      
      return(text)
    
    
     
     #Compose total window   
    def destroy(self):
        self.msg1 = ''
        self.msg2 = ''
        self.points = []
        self.flush_canvas()
        
        
    
        
        
    
        
drag = False
on_alert = False
ix = 0
iy = 0
def dummy_handler(event,x,y,flags, params):
    pass

def handler(event, x, y, flags, params):
    global drag, ix, iy, on_alert
    
    
    gui = params[0]
    
    
    
    if(event == cv.EVENT_RBUTTONUP):
        out = gui.check_within_image(x,y)
        if(drag):
            drag = False
            ix = 0
            iy = 0
            gui.reset_pan()
            gui.reset_alert("Pan Mode Off", old = True)
            
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
            return
        
        out = gui.check_within_points(x,y)
        
        if(on_alert):
        
            if(len(out) > 0):
              name = gui.get_name(out)
              gui.alert(text1 = name, old = True)
            else:
              gui.reset_alert(old = True)
              on_alert = False
        else:
            if(len(out) > 0):
              
              name = gui.get_name(out)
              gui.alert(text1 = name, old = True)
              on_alert = True
            
        
        return
        
        
                
    
    
    
    
    
    if(event == cv.EVENT_LBUTTONUP):
        
        if(drag):  
            return
        
        
        num = gui.check_image_controls(x,y)
        if (num > -1):
            gui.image_position(num)
            return
        
            
        
    
    return
        
            
            
            
            
            
def show(kpoints, gui, im, review = False, remarks = '', with_tool = False, person = ''):

  
  

  xs = kpoints['x'].values
  ys = kpoints['y'].values
  x1s = kpoints['x1'].values
  y1s = kpoints['y1'].values
  types = kpoints['type'].values
  ids = kpoints['id'].values
  pids = kpoints['pid'].values
  hiddens = kpoints['hidden'].values
  annot_types = kpoints['annotation_type'].values
  attrs = kpoints['attr'].values
  b_ids = ids.copy()
  
  for x,y,x1, y1, typ, idx, pid, hidden, annot_type, attr in zip(xs, ys, x1s, y1s, types, ids, pids, hiddens, annot_types, attrs):
    
    
    if(idx == 0):
      att = str(attr)
      typ = str(typ)
      text = att
 
      if(review):
          gui.add_message(text, "Space: Next person in image, t: hide annotations, l: toggle limb, n: next image")
      else:
          gui.add_message(remarks + ": " + text, "Space: Next person, p: Previous, t: toggle landmarks, l: toggle limbs, d: delete person, q: Quit")
      continue
    else:
      point = Point(idx, pid, x, y, x1, y1, typ, hidden, annot_type, attr)
      gui.add_point(point)
    
    if(pid == 0):
      point.is_forehead = True
      for i, idy in enumerate(b_ids):
        
        if(idy == pid):
          
          point.update_parent_coords(xs[i], ys[i])
          typp = types[i]
          
          if(typp == 'Forehead'):
                
                point.p_is_forehead = True
          break
    else:
      point.is_forehead = False
      for i, idy in enumerate(b_ids):
        
        if(idy == pid):
          point.update_parent_coords(xs[i], ys[i])
          typp = types[i]
          
          if(typp == 'Forehead'):
                
                point.p_is_forehead = True
          break
      
        
        
      

def review(kp_dataset_path, accepted_file_path, to_review_path, review_file_path, expunge_file_path, window_size, image_folder, reviewer):
    kp_dataset = pd.read_csv(kp_dataset_path, index_col = False)

    if(os.path.exists(accepted_file_path)):
      accepted = pd.read_csv(accepted_file_path, index_col = False)
      accepted_list = accepted['img_id'].values
    else:
      accepted = pd.DataFrame(columns = ['img_id', 'accepted'])
      accepted.to_csv(accepted_file_path, index = False)
      accepted_list = []

    if(os.path.exists(expunge_file_path)):
      expunged = pd.read_csv(expunge_file_path, index_col = False)
      expunged_list = expunged['img_id'].values
    else:
      expunged = pd.DataFrame(columns = ['img_id', 'expunged'])
      expunged.to_csv(expunge_file_path, index = False)
      expunged_list = []


    if(os.path.exists(to_review_path)):
      tmp = pd.read_csv(to_review_path, index_col = False)
      img_list = tmp['img_id'].values
    else: 
      img_list = kp_dataset["img_id"].unique()
   
    if(os.path.exists(review_file_path)):
          reviewer_dataset = pd.read_csv(review_file_path, index_col = False)
    else:
          reviewer_dataset = pd.DataFrame(columns = ['img_id', 'is_ok', 'remarks', 'reviewer'])

    done = reviewer_dataset['img_id'].values

    gui = Display_GUI(window_size)
    gui.add_image_controls()
    start = input("Enter starting number of first image to review")

    count = 0

    for im in img_list:
      if(count < int(start)):
        count += 1
        continue

      if(im in done):
          continue

      if(im in accepted_list):
        print("File " + im + " has already been accepted. Discuss with annotator" )
        continue
      
      if(im in expunged_list):
        print("File " + im + " has already been expunged. Discuss with annotator" )
        continue


      new_record = {'img_id':[im],'is_ok':[],'remarks':[], 'expunge': [], 'reviewer':[reviewer]}
      
      kp_data = kp_dataset[kp_dataset["img_id"] == im]
      path = os.path.join(image_folder, im)
      
      img = cv.imread(path)
      gui.add_image(img)

      person_list = kp_data['person'].unique()
      cv.namedWindow(im)
      cv.setMouseCallback(im, handler, (gui,) )

      i = 0
      max = len(person_list)
      
      next = True
      while(i < max):
        person = person_list[i]
        


        kpoints = kp_data[kp_data["person"] == person]
        show(kpoints, gui,im, remarks = "|| Showing Person {}".format(person), with_tool = True, person = person)
        jump = False
        stat = False
        while(True):

          window = gui.compose()

          cv.imshow(im, window)
          a = cv.waitKey(20)
          if(a == ord(' ')):

            if(stat):
              gui.reset_alert()
              stat = False
            gui.destroy()
            if( i == max - 1):
                i = 0
            else:
                i += 1
            next = True
            break
          
              
              
          if(a == ord('t') or a == ord('T')):
            gui.toggle_annotations()
            if(stat):
              gui.reset_alert()
              stat = False
          if((a == ord('l') or a == ord('L'))):
            gui.toggle_limb()
            if(stat):
              gui.reset_alert()
              stat = False
          if(a == ord('p') or a == ord('P')):
            gui.destroy()
            if(i == 0):
              i = max - 1
            else:
              i -= 1
            next = False
            break

          if(a == ord('q') or a == ord('Q')):
            gui.destroy()
            next = False
            jump = True
            break

        if(jump):
            break





      cv.destroyAllWindows()
      ok = input("Is annotation satisfactory? (y/n/e/s). e to expunge ; s to skip review ")
      if(ok == 's'):
         pass
      else:
          if (ok == 'y'):
            new_record['is_ok'].append(True)
            new_record['expunge'].append(False)
            
          else:
            new_record['is_ok'].append(False)
          if(ok == 'n'):
              remarks = input("Any remarks? ")
              new_record['remarks'].append(remarks)
              new_record['expunge'].append(False)        
          else:
            new_record['remarks'].append('Accepted')
          
          
          
          if(ok == 'y'):
              accepted_record = {'img_id':[im], 'accepted':[True]}
              accepted_record = pd.DataFrame(accepted_record)
              accepted = accepted.append(accepted_record, ignore_index = True)

          if(ok == 'e'):
              expunged_record = {'img_id':[im], 'expunged':[True]}
              expunged_record = pd.DataFrame(expunged_record)
              expunged = expunged.append(expunged_record, ignore_index = True)
              new_record['expunge'].append(True)
     
          new_record = pd.DataFrame(new_record)
          reviewer_dataset = reviewer_dataset.append(new_record, ignore_index = True)
      
      b = input("show next image in folder? (y/n) ")

      if(b == 'y'):

        continue
      else: 
        break

    reviewer_dataset.to_csv(review_file_path, index = False)
    accepted.to_csv(accepted_file_path, index = False)
    expunged.to_csv(expunge_file_path, index = False)




