import numpy as np
import pandas as pd
import cv2 as cv
import sys
import string
import os
from kp_package.annotation_structure import *
from kp_package.annotation_gui import *



landmarks = ["Root", "Forehead", "Left Eye", "Left Ear", "Left Shoulder", "Left Hip", "Right Eye", "Right Ear", "Right Shoulder", "Right Hip", "Nose", "Left Elbow", "Left Knee", "Right Elbow", "Right Knee", "Left Wrist", "Left Ankle", "Right Wrist", "Right Ankle", "Mouth", "Crown", "Vaahan", "Article_Left", "Article_Right"]
limbs = {"Root":[1], "Forehead":[10,19,2,6,3,7,20, 4,8,5,9,21], "Left Shoulder":[11], "Left Elbow": [15], "Left Hip":[12], "Left Knee": [16], "Right Shoulder":[13], "Right Elbow": [17], "Right Hip":[14], "Right Knee": [18], "Left Wrist" : [22], "Right Wrist" : [23]}
possible_duplicates = [1,11,12,13,14]



        
#For collecting attribute for each person
def keyboard_input(gui, person_id, name = 'Preliminary View'):
    if(person_id == 0):
        msg = "Start Annotation. Enter Attributes for the first person ('-1' to escape)"
    else:
        msg = "Starting New Person. Enter Attributes (-1 to escape)"
    text = ""
    letters = string.printable
    blip = 0
    while True:
        if len(text) == 0 and (blip < 25):
            disp = "__"
        elif len(text) == 0 and (blip >= 25):
            disp = ''
        else:
            disp = text
        blip += 1
        if(blip >= 50):
            blip = 0
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

#Some global Variables

drag = False		#Whether image pane is in pan mode

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
    if(state == 'draw_bbox'):
        bbox = True
    else:
        bbox = False
    if(annot.next_link.get_annotation_type() == 'Bbox'):
        type_bbox = True
    else:
        type_bbox = False
    
    if((event == cv.EVENT_RBUTTONUP) and not bbox):
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
            return

        if(bbox):
            out = gui.check_within_image(x,y)
            if(out):
                
                gui.update_bbox(x,y)
                
    
    
    
    
    
    if(event == cv.EVENT_LBUTTONUP):
        
        if(drag):
            
            return
        



        if(gui.dialog_on):
            num = gui.check_within_buttons(x,y)
            if(num > -1):
                
                if(num == 0):
                    out = annot.do_confirm(num)
                    gui.reset_bbox_on()
                    
                    
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), text)
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), text)
                    gui.reset_dialog()
                    
                    
                    
                    
                elif(num == 1):
                    out = annot.do_confirm(num)
                    gui.reset_bbox_on()
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), "Selection Recorded")
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), "Selection Recorded")
                    gui.reset_dialog()
                    
                    
                else:
                    out = annot.dont_confirm()
                    gui.reset_bbox_on()
                    if(out == 1):
                        gui.add_message("Select another " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), "Selection Cancelled")
                    else:
                        gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), "Cancelled")
                    gui.reset_dialog()
                    
                gui.flush_canvas()
                  
                gui.add_elements(annot.parent_link)
                  
            return
        
        
        
        gui.flush_canvas()
        if(not bbox):
          num = gui.check_within(x,y)
          if num > -1:
            
            
            annot.set_child(num)
            
            if(annot.next_link.get_type() == "Root"):
                    gui.add_message("Annotation Complete" "ANN")
                    
                    return
            
    
            gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), "")
            gui.add_elements(annot.parent_link)
            
        
        
          num = gui.check_image_controls(x,y)
          if (num > -1):
            gui.image_position(num)
            
        out = gui.check_within_image(x,y)
        x1,y1 = gui.rescale_coords(x,y)
        
        if(out):
            gui.current_selx, gui.current_sely = x1, y1
            annot.do_select(x1, y1)
            if(annot.get_state() == 'confirm'):
                gui.add_dialog(x,y,is_bbox = type_bbox)
                if(type_bbox):
                    gui.freeze_bbox(x, y)
            elif(annot.get_state() == 'draw_bbox'):
                gui.set_bbox_on(x, y)
                
            
     
      
            
            
            
        
            
        
        
def tool_GUI(img_name, All_annotations, name = 'View', img = None, window_size = (1028,768), next_id = 0):
  
  gui = Gui(window_size)
  person_id = next_id
  added = False
  added_count = 0
  
  
  gui.add_image(img)
  gui.add_image_controls()
  
  
  
  
  while(True):
    
    annot = Annotation_GUI(landmarks, limbs, possible_duplicates, annotation_types, person_id = person_id, img_id = img_name)
    
    
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
        
        gui.cx, gui.cy, gui.cx1, gui.cy1, gui.cz, gui.cz1  = annot.traverse(annot.current_parent)
        window = gui.compose()
            
        
        cv.imshow(name, window)
        
            
        a = cv.waitKey(20)
        
        if(annot.get_state() == 'confirm' and a == ord(' ')):
            out = annot.do_confirm(0)
            gui.reset_bbox_on()
            
            
            if(out == 1):
                    gui.add_message("Select another " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            else:
                    gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            gui.reset_dialog()
            
            gui.flush_canvas()
                  
            gui.add_elements(annot.parent_link)
        
        if(annot.get_state() == 'confirm' and (a == ord('h') or a == ord('H'))) and (annot.next_link.get_annotatio_type() != 'Bbox'):
            out = annot.do_confirm(1)
            gui.reset_bbox_on()
            
                    
                    
            if(out == 1):
                    gui.add_message("Select another " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            else:
                    gui.add_message("Select a " + annot.next_link.get_type() + " [" + annot.next_link.get_annotation_type() +"] " + " connected to highlighted " + annot.parent_link.get_type(), attr + " : Press q at any time to quit current person annotation")
            gui.reset_dialog()
            
            gui.flush_canvas()
                  
            gui.add_elements(annot.parent_link)
            
        if ((a == ord('q') or a == ord('Q')) and complete):
            to_save = False
            break
        
        if ((a == ord('q') or a == ord('Q')) and not complete):
            gui.reset_bbox_on()
            gui.add_message("Annotation is incomplete", "'a': Save and add person, 's': Save and Quit, 'x' Quit without saving, 'n': add person without saving")
            alert = True
            
        elif(a == ord('a') or a == ord('A')):
            to_save = True
            more = True
            added_count += 1
            break
        
        elif(a == ord('s') or a == ord('S')):
            to_save = True
            more = False
            added_count += 1
  
            break
        
        elif((a == ord('x') or a == ord('X')) and alert):
            to_save = False
            more = False
            break
            
        elif((a == ord('n') or a == ord('N')) and alert):
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