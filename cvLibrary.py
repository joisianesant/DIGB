import os
import numpy as np
import cv2
import json
from kivy.graphics.texture import Texture
import matplotlib.pyplot as plt

from ultralytics import YOLO, checks
#from pyzbar.pyzbar import decode
import math
import numpy as np
import gc
import time







class vision():
    image = np.mat
    kivy_texture = any


    def opencv2kivyImage(self, img_ori):
        img = cv2.flip(img_ori, 0)
        data = img.tostring() #tobytes()
        
        #self.cvImage = img

        if(len(img.shape) == 2):
            col, row = img.shape
            texture = Texture.create(size=( row, col), colorfmt='luminance')#'luminance'
            texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="luminance")
        else:
            col, row, c = img.shape
            texture = Texture.create(size=( row, col), colorfmt='bgr')
            texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="bgr")

        self.kivy_texture = texture

        return texture
    
    def read_image(self, imgsrc):
        return cv2.imread(imgsrc)
    
    def write_image(self, imgsrc, imgfilename):
        try:
            result = cv2.imwrite(imgfilename, imgsrc)

            return result
        except:
            return False
        

    def draw_crosshair(self, _img, x, y, homo):
        try:
            if len(homo[0]) > 0:
                pts1 = np.float32([ [x,y] ]).reshape(-1,1,2)
                
                pts1 = self.pts_homography(pts1, homo)
                

                # Drawing the lines 
                cv2.line(_img, (int(pts1[0][0][0])-20, int(pts1[0][0][1])), (int(pts1[0][0][0])+20, int(pts1[0][0][1])), (0, 255, 0), 5) 
                cv2.line(_img, (int(pts1[0][0][0]), int(pts1[0][0][1])-20), (int(pts1[0][0][0]), int(pts1[0][0][1])+20), (0, 255, 0), 5) 
        except:
            cv2.line(_img, (x-20, y), (x+20, y), (0, 255, 0), 5) 
            cv2.line(_img, (x, y-20), (x, y+20), (0, 255, 0), 5) 
        


    #draw selected object
    def drawSelectedObject(self, _img, _obj, offx, offy, offa, homo):
        
        font = cv2.FONT_HERSHEY_DUPLEX     

        try:
            box_x2 = (_obj['box_x']/2)
            box_y2 = (_obj['box_y']/2)
        except:
            box_x2 = 0
            box_y2 = 0

        #dst = cv2.perspectiveTransform(pts, mtrx)
        #dst = cv2.perspectiveTransform(pts, mtrx)
        x1 = _obj['x']
        y1 = _obj['y']
        w = _obj['box_x']
        h = _obj['box_y']
        x2 = x1+w
        y2 = y1+h
        try:
            pts = np.float32([ [int(x1),int(y1)] ]).reshape(-1,1,2)
            pts = self.pts_homography(pts,homo)
            x1 = pts[0][0][0]-(float(w)/2)
            y1 = pts[0][0][1]-(float(h)/2)
            x2 = pts[0][0][0]+(float(w)/2)
            y2 = pts[0][0][1]+(float(h)/2)
        except:
            pass

        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        if(_obj['pose'].find('FID') > -1):            
            draw_color = (0,155,155)  
        else:
            draw_color = (255,0,255)

        cv2.rectangle(_img, (x1, y1), (x2,y2), draw_color,3)
        #obj = np.float32([ [_obj['x']-box_x2,_obj['y']-box_y2], [_obj['x']+box_x2,_obj['y']-box_y2], [_obj['x']+box_x2,_obj['y']+box_y2], [_obj['x']-box_x2,_obj['y']+box_y2] ])
        #obj = np.float32([ [(offx+_obj['x'])-box_x2,(offy-_obj['y'])-box_y2], [(offx+_obj['x'])+box_x2,(offy-_obj['y'])-box_y2], [(offx+_obj['x'])+box_x2,(offy-_obj['y'])+box_y2], [(offx+_obj['x'])-box_x2,(offy-_obj['y'])+box_y2] ])
        #_img = cv2.polylines(_img,[np.int32(obj)],True,(255,0,255),6, cv2.FILLED)
        try:
            cv2.putText(_img, _obj['pose'], (np.int32(x1), np.int32(y1)), font, 1, (255,0,255), 2, cv2.LINE_AA)
        except:
            pass
        



    # Draw matche bounding box
    def drawObjects_bk(self, _img, _objs, isAnnotation, offx, offy, offa):
        h,w, = _img.shape[:2]
        pts = np.float32([ [[0,0]],[[0,h-1]],[[w-1,h-1]],[[w-1,0]] ])
        #dst = cv2.perspectiveTransform(pts, mtrx)
        img = cv2.polylines(_img,[np.int32(pts)],True,(0,255,0),3, cv2.LINE_AA)

        font = cv2.FONT_HERSHEY_DUPLEX        

        if(isAnnotation):
            for i in _objs['annotation']['object']:    
            
                #dst = cv2.perspectiveTransform(pts, mtrx)
                if(i['pose'].find('FID') > -1):
                    obj = np.float32([ [i['points'][0][0],i['points'][0][1]],[i['points'][1][0],i['points'][0][1]],[i['points'][1][0],i['points'][1][1]],[i['points'][0][0],i['points'][1][1]] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,0),3, cv2.LINE_AA)
                    cv2.putText(_img, i['label'], (np.int32(i['points'][0][0]),np.int32(i['points'][0][1])), font, 1, (255,255,0), 2, cv2.LINE_AA)
                elif(len(i['bndbox']) > 2):
                    obj = []
                    obj.append( [ np.float32(i['bndbox']['xmin']), np.float32(i['bndbox']['ymin'])] )
                    obj.append( [ np.float32(i['bndbox']['xmin']), np.float32(i['bndbox']['ymax'])] )
                    obj.append( [ np.float32(i['bndbox']['xmax']) , np.float32(i['bndbox']['ymax']) ] )
                    obj.append( [ np.float32(i['bndbox']['xmax']), np.float32(i['bndbox']['ymin'])] )
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,128),3, cv2.LINE_AA)
                    cv2.putText(_img, i['pose'], (np.int32(i['bndbox']['xmin']),np.int32(i['bndbox']['ymin'])), font, 1, (255,255,0), 2, cv2.LINE_AA)
                else:
                    obj = np.float32([ i['bndbox']['xmin'],i['bndbox']['ymin']],[i['bndbox']['xmax'],i['bndbox']['ymin']],[i['bndbox']['xmax'],i['bndbox']['xmax']],[i['bndbox']['xmin'],i['bndbox']['ymax'] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,255),3, cv2.LINE_AA)
                    cv2.putText(_img, i['pose'], (np.int32(i['bndbox']['xmin']),np.int32(i['bndbox']['ymin'])), font, 1, (0,255,0), 2, cv2.LINE_AA)
        else:
            #self.drawObjects_json(_img, _objs)
            for i in _objs:    
                try:
                    box_x2 = (i['box_x']/2)
                    box_y2 = (i['box_y']/2)
                except:
                    box_x2 = 0
                    box_y2 = 0

                #dst = cv2.perspectiveTransform(pts, mtrx)
                if(i['pose'].find('FID') > -1):
                    obj = np.float32([ [(offx+i['x'])-box_x2,(offy-i['y'])-box_y2], [(offx+i['x'])+box_x2,(offy-i['y'])-box_y2], [(offx+i['x'])+box_x2,(offy-i['y'])+box_y2], [(offx+i['x'])-box_x2,(offy-i['y'])+box_y2] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(0,255,255),3, cv2.LINE_AA)
                    try:
                        cv2.putText(_img, i['pose'], (np.int32((offx+i['x'])-box_x2),np.int32((offy-i['y'])-box_y2)), font, 1, (0,255,255), 2, cv2.LINE_AA)
                    except:
                        pass
                else:
                    #obj = np.float32([ [i['x']-box_x2,i['y']-box_y2], [i['x']+box_x2,i['y']-box_y2], [i['x']+box_x2,i['y']+box_y2], [i['x']-box_x2,i['y']+box_y2] ])
                    obj = np.float32([ [(offx+i['x'])-box_x2,(offy-i['y'])-box_y2], [(offx+i['x'])+box_x2,(offy-i['y'])-box_y2], [(offx+i['x'])+box_x2,(offy-i['y'])+box_y2], [(offx+i['x'])-box_x2,(offy-i['y'])+box_y2] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,0),3, cv2.LINE_AA)
                    try:
                        cv2.putText(_img, i['pose'], [np.int32((offx+i['x'])-box_x2),np.int32((offy-i['y'])-box_y2)], font, 1, (255,255,0), 2, cv2.LINE_AA)
                    except:
                        pass



    # Draw matche bounding box
    def drawObjects(self, _img, _objs, isAnnotation, offx, offy, offa, homo):
       

        font = cv2.FONT_HERSHEY_DUPLEX        

        if(isAnnotation):
            for i in _objs['annotation']['object']:    
            
                #dst = cv2.perspectiveTransform(pts, mtrx)
                if(i['pose'].find('FID') > -1):
                    obj = np.float32([ [i['points'][0][0],i['points'][0][1]],[i['points'][1][0],i['points'][0][1]],[i['points'][1][0],i['points'][1][1]],[i['points'][0][0],i['points'][1][1]] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,0),3, cv2.LINE_AA)
                    cv2.putText(_img, i['label'], (np.int32(i['points'][0][0]),np.int32(i['points'][0][1])), font, 1, (255,255,0), 2, cv2.LINE_AA)
                elif(len(i['bndbox']) > 2):
                    obj = []
                    obj.append( [ np.float32(i['bndbox']['xmin']), np.float32(i['bndbox']['ymin'])] )
                    obj.append( [ np.float32(i['bndbox']['xmin']), np.float32(i['bndbox']['ymax'])] )
                    obj.append( [ np.float32(i['bndbox']['xmax']) , np.float32(i['bndbox']['ymax']) ] )
                    obj.append( [ np.float32(i['bndbox']['xmax']), np.float32(i['bndbox']['ymin'])] )
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,128),3, cv2.LINE_AA)
                    cv2.putText(_img, i['pose'], (np.int32(i['bndbox']['xmin']),np.int32(i['bndbox']['ymin'])), font, 1, (255,255,0), 2, cv2.LINE_AA)
                else:
                    obj = np.float32([ i['bndbox']['xmin'],i['bndbox']['ymin']],[i['bndbox']['xmax'],i['bndbox']['ymin']],[i['bndbox']['xmax'],i['bndbox']['xmax']],[i['bndbox']['xmin'],i['bndbox']['ymax'] ])
                    _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,255),3, cv2.LINE_AA)
                    cv2.putText(_img, i['pose'], (np.int32(i['bndbox']['xmin']),np.int32(i['bndbox']['ymin'])), font, 1, (0,255,0), 2, cv2.LINE_AA)
        else:
            #self.drawObjects_json(_img, _objs)
            for i in _objs:    
                try:
                    box_x2 = (i['box_x']/2)
                    box_y2 = (i['box_y']/2)
                except:
                    box_x2 = 0
                    box_y2 = 0

                #dst = cv2.perspectiveTransform(pts, mtrx)
                x1 = i['x']
                y1 = i['y']
                w = i['box_x']
                h = i['box_y']
                x2 = x1+w
                y2 = y1+h
                try:
                    pts = np.float32([ [int(x1),int(y1)] ]).reshape(-1,1,2)
                    pts = self.pts_homography(pts,homo)
                    x1 = pts[0][0][0]-(float(w)/2)
                    y1 = pts[0][0][1]-(float(h)/2)
                    x2 = pts[0][0][0]+(float(w)/2)
                    y2 = pts[0][0][1]+(float(h)/2)
                except:
                    pass

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                if(i['pose'].find('FID') > -1):            
                    draw_color = (0,255,255)  
                else:
                    draw_color = (255,255,0)

                cv2.rectangle(_img, (x1, y1), (x2,y2), draw_color,3)

                try:
                    cv2.putText(_img, i['pose'], (np.int32((x1)),np.int32((y1)-5)), font, 1, draw_color, 2, cv2.LINE_AA)

                    conf = math.ceil((i['conf'][0] * 100)) / 100
                    ref_class = int(i.cls[0])
                    cv2.putText(_img, i[ref_class]+': '+str(conf), (x1, y1), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.35, color=(0, 255, 0),thickness=1)
                    
                except:
                    pass





    # Draw matche bounding box
    def drawObjects_json(self, _img, _objs):
        h,w, = _img.shape[:2]
        pts = np.float32([ [[0,0]],[[0,h-1]],[[w-1,h-1]],[[w-1,0]] ])
        #dst = cv2.perspectiveTransform(pts, mtrx)
        img = cv2.polylines(_img,[np.int32(pts)],True,(0,255,0),3, cv2.LINE_AA)

        font = cv2.FONT_HERSHEY_DUPLEX        

        for i in _objs['shapes']:    
            
            #dst = cv2.perspectiveTransform(pts, mtrx)
            if(i['label'].find('FID') > -1):
                obj = np.float32([ [i['points'][0][0],i['points'][0][1]],[i['points'][1][0],i['points'][0][1]],[i['points'][1][0],i['points'][1][1]],[i['points'][0][0],i['points'][1][1]] ])
                _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,0),3, cv2.LINE_AA)
                cv2.putText(_img, i['label'], (int(i['points'][0][0]),int(i['points'][0][1])), font, 1, (255,255,0), 2, cv2.LINE_AA)
            elif(len(i['points']) > 2):
                obj = []
                for p in i['points']:
                    obj.append( np.float32( [p[0],p[1]] ) )
                _img = cv2.polylines(_img,[np.int32(obj)],True,(255,255,0),3, cv2.LINE_AA)
                cv2.putText(_img, i['label'], (int(i['points'][0][0]),int(i['points'][0][1])), font, 1, (255,255,0), 2, cv2.LINE_AA)
            else:
                obj = np.float32([ [i['points'][0][0],i['points'][0][1]],[i['points'][1][0],i['points'][0][1]],[i['points'][1][0],i['points'][1][1]],[i['points'][0][0],i['points'][1][1]] ])
                _img = cv2.polylines(_img,[np.int32(obj)],True,(0,255,0),3, cv2.LINE_AA)
                cv2.putText(_img, i['label'], (int(i['points'][0][0]),int(i['points'][0][1])), font, 1, (0,255,0), 2, cv2.LINE_AA)


    


    def roiSelectModelCV(self, img, showCrosshair, fromCenter, modelName):
        #Adjust the window
        #cv2.namedWindow(modelName, cv2.WINDOW_FULLSCREEN)
        #cv2.resizeWindow(modelName, 1000, 800)
        cv2.namedWindow(modelName, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(modelName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        #cv2.moveWindow(modelName, 200, 200)
        
        # Create a dictionary to store the image, window name, and ROI
        param = {'image': img, 'window_name': modelName}

        # Set the mouse callback function for the window
        #cv2.setMouseCallback(modelName, self.onmouse) #self.select_roi_callback, param)

        
        rois = cv2.selectROIs(modelName, img, fromCenter=fromCenter, showCrosshair=showCrosshair)

        

       

        cv2.destroyWindow(modelName)


        return rois
    


    def roiSelectModelProduct(self, img, showCrosshair, fromCenter, modelName):
        #Adjust the window
       
        cv2.namedWindow(modelName, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(modelName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Create a dictionary to store the image, window name, and ROI
        param = {'image': img, 'window_name': modelName}

        # Set the mouse callback function for the window
        #cv2.setMouseCallback(modelName, self.onmouse) #self.select_roi_callback, param)

        
        roi = cv2.selectROI(modelName, img, fromCenter=fromCenter, showCrosshair=showCrosshair)


        cv2.destroyWindow(modelName)


        return roi





    #
    def onmouse(event, x, y, flags, param):
        global drag_start, sel
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if event == cv2.EVENT_LBUTTONDOWN:
            drag_start = x, y
            sel = 0,0,0,0
        elif event == cv2.EVENT_LBUTTONUP:
            if sel[2] > sel[0] and sel[3] > sel[1]:
                patch = gray[sel[1]:sel[3],sel[0]:sel[2]]
                result = cv2.matchTemplate(gray,patch,cv2.TM_CCOEFF_NORMED)
                result = np.abs(result)**3
                _val, result = cv2.threshold(result, 0.01, 0, cv2.THRESH_TOZERO)
                result8 = cv2.normalize(result,None,0,255,cv2.NORM_MINMAX,cv2.CV_8U)
                cv2.imshow("result", result8)
            drag_start = None
        elif drag_start:
            #print flags
            if flags & cv2.EVENT_FLAG_LBUTTON:
                minpos = min(drag_start[0], x), min(drag_start[1], y)
                maxpos = max(drag_start[0], x), max(drag_start[1], y)
                sel = minpos[0], minpos[1], maxpos[0], maxpos[1]
                img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                cv2.rectangle(img, (sel[0], sel[1]), (sel[2], sel[3]), (0,255,255), 1)
                cv2.imshow("gray", img)
            else:
                print("selection is complete")
                drag_start = None

    
    # Define a callback function to handle mouse events
    def select_roi_callback(event, x, y, flags, params):
        global rect, scale, x_offset, y_offset, resized_image, new_cols, new_rows
    
        if event == cv2.EVENT_LBUTTONDOWN:
            # Set the center of the rotated rectangle
            rect = [(x, y)]
    
        elif event == cv2.EVENT_LBUTTONUP:
            # Set the size and angle of the rotated rectangle
            rect.append((x, y))
            rect.append(45)  # Set the angle to 45 degrees
        
            # Draw the rotated rectangle on the image
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(event.image, [box], 0, (0, 0, 255), 2)
            cv2.imshow('image', event.image)
        
            # Select the ROI
            roi = cv2.selectROI('image', fromCenter=False, showCrosshair=True)
        
            # Crop the ROI from the image
            cropped_image = event.image[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
        
            # Display the cropped image
            cv2.imshow('Cropped Image', cropped_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
        elif event == cv2.EVENT_MOUSEWHEEL:
            # Update the scaling factor for zooming
            scale += flags * 0.1
            scale = max(scale, 0.1)
            scale = min(scale, 3)
        
            # Resize the image
            rows, cols, _ = event.image.shape
            new_rows, new_cols = int(rows * scale), int(cols * scale)
            resized_image = cv2.resize(event.image, (new_cols, new_rows))
        
            # Update the offset for translating the image
            x_offset = max(x_offset, new_cols - cols)
            y_offset = max(y_offset, new_rows - rows)
            x_offset = min(x_offset, 0)
            y_offset = min(y_offset, 0)
        
            # Display the zoomed and translated image
            translated_image = resized_image[-y_offset:(new_rows-rows-y_offset), -x_offset:(new_cols-cols-x_offset)]
            cv2.imshow('image', translated_image)
    
        elif event == cv2.EVENT_MOUSEMOVE:
            # Update the offset for translating the image
            if flags == 1:
                x_offset += x - params[0]
                y_offset += y - params[1]
                x_offset = max(x_offset, new_cols - cols)
                y_offset = max(y_offset, new_rows - rows)
                x_offset = min(x_offset, 0)
                y_offset = min(y_offset, 0)
            
                # Display the zoomed and translated image
                translated_image = resized_image[-y_offset:(new_rows-rows-y_offset), -x_offset:(new_cols-cols-x_offset)]
                cv2.imshow('image', translated_image)
    
        elif event == cv2.EVENT_LBUTTONUP:
            # Save the mouse position for updating the offset
            params[0], params[1] = x, y
            


    def draw_inference_results(self, img, results, classes):
        for r in results:
            boxes = r.boxes
            for box in boxes:
                
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2,y2), (255,0,255),3)

                conf = math.ceil((box.conf[0] * 100)) / 100

                ref_class = int(box.cls[0])
                cv2.putText(img, classes[ref_class]+': '+str(conf), (x1, y1), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.35, color=(0, 255, 255),thickness=1)


    def draw_inference_results_best(self, img, results, classes, homo):
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                
                
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2,y2), (255,0,255),3)

                conf = math.ceil((box.conf[0] * 100)) / 100

                ref_class = int(box.cls[0])
                cv2.putText(img, classes[ref_class]+': '+str(conf), (x1, y1), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.35, color=(0, 255, 255),thickness=1)
                break


    def draw_aligned_product(self, img, results, classes, homo):
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1 = 0
                y1 = 0
                x, y, w, h = box.xywh[0]
                try:
                    pts = np.float32([ [int(x1),int(y1)] ]).reshape(-1,1,2)
                    pts = self.pts_homography(pts,homo)
                    x1 = pts[0][0][0]#-(float(w)/2)
                    y1 = pts[0][0][1]#-(float(h)/2)
                    x2 = pts[0][0][0]+(float(w))
                    y2 = pts[0][0][1]+(float(h))
                except:
                    pass
                
                
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(img, (x1, y1), (x2,y2), (255,0,255),3)

                conf = math.ceil((box.conf[0] * 100)) / 100

                ref_class = int(box.cls[0])
                cv2.putText(img, classes[ref_class]+': '+str(conf), (x1, y1), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.35, color=(0, 255, 0),thickness=1)
                break


    def cut_comp(self, img, x, y, a, boxX, boxY, homo):
        try:
            pts = np.float32([ [int(x),int(y)] ]).reshape(-1,1,2)
            pts = self.pts_homography(pts,homo)
            x = pts[0][0][0]
            y = pts[0][0][1]
        finally:
            x1 = int(x-(boxX/2)) 
            y1 = int(y-(boxY/2)) 
            x2 = int(x+(boxX/2)) 
            y2 = int(y+(boxY/2))

            crop = img[y1:y2, x1:x2] 

        return crop

    def cut_product(self, img, x1, y1, x2, y2):
        

        crop = img[y1:y1+y2, x1:x1+x2] 
        #cv2.imshow('tes',crop)
        return crop


    def draw_matches(self, img, positives, falsepositives, negatives, classes, homo):
        
        color=(0, 255, 0)
        self.draw_with_homo(img, positives, color, homo)
        

        #False positives
        #color=(0, 255, 255)
        #self.draw_with_homo(img, falsepositives, color, homo)
        for box in falsepositives:
            x1 = int(box['x']-(box['box_x']/2)) 
            y1 = int(box['y']-(box['box_y']/2)) 
            x2 = int(box['x']+(box['box_x']/2)) 
            y2 = int(box['y']+(box['box_y']/2)) 
            #x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cv2.rectangle(img, (x1, y1), (x2,y2), (0,255,255),3)

            conf = math.ceil((box['conf'] * 100)) / 100

            ref_class = box['model']
            cv2.putText(img, ref_class+': '+str(conf), (x1, y1-5), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.5, color=(0, 255, 255),thickness=1)

        #Negatives
        color=(0, 0, 255)
        self.draw_with_homo(img, negatives, color, homo)
        
    


    def draw_with_homo(self, img, components, color, homo):
        for i in components: 
            x1 = i['x']
            y1 = i['y']
            w = i['box_x']
            h = i['box_y']
            x2 = x1+w
            y2 = y1+h
            try:
                pts = np.float32([ [int(x1),int(y1)] ]).reshape(-1,1,2)
                pts = self.pts_homography(pts,homo)
                x1 = pts[0][0][0]-(float(w)/2)
                y1 = pts[0][0][1]-(float(h)/2)
                x2 = pts[0][0][0]+(float(w)/2)
                y2 = pts[0][0][1]+(float(h)/2)
            except:
                pass

            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            

            cv2.rectangle(img, (x1, y1), (x2,y2), color,3)

            try:
                cv2.putText(img, i['pose'], (np.int32((x1)),np.int32((y1)-5)), cv2.FONT_HERSHEY_TRIPLEX, 1, color, 2, cv2.LINE_AA)

                conf = math.ceil((i['conf'][0] * 100)) / 100
                ref_class = int(i.cls[0])
                cv2.putText(img, i[ref_class]+': '+str(conf), (x1, y1), cv2.FONT_HERSHEY_TRIPLEX, (255,255,0), fontScale=.35, thickness=1)
                
            except:
                pass


    def draw_selected_inference(self, img, box, classes):
        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cv2.rectangle(img, (x1, y1), (x2,y2), (0,255,255),3)

        conf = math.ceil((box.conf[0] * 100)) / 100

        ref_class = int(box.cls[0])
        cv2.putText(img, classes[ref_class]+': '+str(conf), (x1, y1), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=.35, color=(255, 0, 0),thickness=1)


    def inference_ai_model(self, model_source, image_inference, classNames):
        try:
            tstart = time.time()
            img = image_inference #cv2.imread(image_inference)

        
            model = YOLO(model_source)
            tmodel = time.time()


            #classNames = [ 'CES-SMALL', 'CES-MEDIUM']#['CE-MEDIUM0', 'CE-MEDIUM270', 'CE-SMALL0', 'CE-SMALL270', 'FID-CROSS', 'HDMI90', 'MIC90', 'RJ45', 'TYPE_C', 'USB270', 'USB90', 'VGA90']

            #images = [img, img]
            results = model.predict(img) 
            tinference = time.time()
        
            classNames = results[0].names
            self.draw_inference_results(img, results, classNames)
            tdraw = time.time() 

        except:
            return None, classNames, 0, 0, 0


        gc.collect()

        return results, classNames, tmodel-tstart, "{:.2f}".format(tinference-tmodel), time.time()-tstart
        #cv2.imshow("Results", img)
        #cv2.waitKey(0)


    def decode(self, image):
        try:
            decodedObjects = None#decode(image)

            self.displaycodes(image, decodedObjects)

            return decodedObjects
        except:
            return None


    #def barcode_detect(self, image):
    #    bar_detect = cv2.


    def displaycodes(self, im, decodedObjects):
 
        # Loop over all decoded objects
        for decodedObject in decodedObjects:
            points = decodedObject.polygon
 
            # If the points do not form a quad, find convex hull
            if len(points) > 4 :
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else :
                hull = points
 
            # Number of points in the convex hull
            n = len(hull)
 
            # Draw the convext hull
            for j in range(0,n):
                hull[j] = (int(hull[j][0]), int(hull[j][1]))
                hull[(j+1) % n] = (int(hull[(j+1) % n][0]), int(hull[(j+1) % n][1]))
                cv2.line(im, hull[j], hull[ (j+1) % n], (255,0,0), 3)

    def usb_cam_initialize(self, index):
        cam = cv2.VideoCapture(index)
        return cam

    def usb_cam_capture(self, cam):
        for i in range(5):
            ret, frame = cam.read()

        return frame
    

    


    def iou_numpy(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = np.maximum(boxA[0], boxB[0])
        yA = np.maximum(boxA[1], boxB[1])
        xB = np.minimum(boxA[2], boxB[2])
        yB = np.minimum(boxA[3], boxB[3])
	    # compute the area of intersection rectangle
        interArea = np.maximum(0, xB - xA + 1) * np.maximum(0, yB - yA + 1)
	    # compute the area of both the prediction and ground-truth
	    # rectangles
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
	    # compute the intersection over union by taking the intersection
	    # area and dividing it by the sum of prediction + ground-truth
	    # areas - the interesection area
        
        iou = interArea / float(boxAArea + boxBArea - interArea)
	    
        # return the intersection over union value
        return iou
    


    def check_program(self, source, results, side, programList, classes, *args):
        tprogram = time.time()
        #if(side == 'top'):
        #    programList = self.programInfo1['board']['components']
        #else:
        
        programList = programList['board']['components']

        try:
            positives = []
            falsepositives = []
            negatives = []
            rboxes = results[0].boxes.data.cpu().data.numpy().tolist() #tolist()
            cont = 0
            for c in programList:
                cont += 1
                if(c['inspect'] == True):
                    found = False
                    _result = []
                    rem = []
                    iou_min = 0.3
                    iou_max = 0
                    np_count = 0
                    for r in rboxes:
                        x1 = c['x']-(c['box_x']/2)
                        y1 = c['y']-(c['box_y']/2)
                        x2 = c['x']+(c['box_x']/2)
                        y2 = c['y']+(c['box_y']/2)
                        #iou2 = self.check_comp_np( [r[0],r[1],r[2],r[3]], [x1,y1,x2,y2])
                        iou = self.iou_numpy( np.array([r[0],r[1],r[2],r[3]]), np.array([x1,y1,x2,y2]))

                        if(iou > iou_max):
                            iou_max = iou


                        if(iou > iou_min or (r[0]<x1 and r[2]>x2 and r[1]<y1 and r[3]>y2 ) ): #intersection
                            _result.append( {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': r[4], 'cover': iou } )
                            r.append(iou)
                            rem.append(r)
                            found = True
                            iou_min = iou
                            

                        np_count += 1                      
                            
                            
                    if(not found):
                        _result = {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': 0.0, 'cover': 0.0} 
                        negatives.append(_result)
                    else:
                        if(len(_result) == 1):
                            if(c['model'] == classes[int(rem[0][5])]):
                                positives.append(_result[0])
                                rboxes.remove( rem[0] )
                            else:
                                _result[0]['model'] = classes[int(rem[0][5])]
                                #_result[0]['pose'] = '(???)'
                                _result[0]['conf'] = 0.0
                                negatives.append(_result[0])
                                
                                #falsepositives.append(_result[0])
                            #rboxes.remove( rem[0])
                        else:
                            cont = 0
                            found = False
                            for rr in rem:
                                if(classes[int(rr[5])] == c['model']):
                                    __result = {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': rr[4], 'cover': rr[6]} 
                                    positives.append(__result)
                                    rboxes.remove( rr )
                                    #rem.remove( rr )
                                    found = True
                                    break
                                cont+=1

                            if (not found):
                                __result = {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': 0.0, 'cover': 0.0} 
                                negatives.append(__result)
                                
            


                    #self.negatives
            if(len(rboxes)>0):
                for j in rboxes:
                    _found = False
                    try:
                        _n = negatives.index(j)
                        _found = True
                    except:
                        pass

                    try:
                        _f = falsepositives.index(j)
                        _found = True
                    except:
                        pass
                    
                    if(not _found):
                        box_xi = int((j[2])-(j[0]))
                        box_yi = int(j[3]-j[1])
                        xi1 = int(j[0]+(box_xi/2))
                        yi1 = int(j[1]+(box_yi/2))
                        _result = {'x': xi1, 'y': yi1, 'a': 0, 'box_x': box_xi, 'box_y': box_yi, 'pose': '(???)', 'model': classes[int(j[5])], 'type': '', 'conf': j[4], 'cover': 0 } 
                        falsepositives.append(_result)


            
            drawingImage = self.image.copy()
            self.draw_matches( drawingImage, positives, falsepositives, negatives, classes)
            if(side == 'top'):
                self.source1 = drawingImage
            else:
                self.source2 = drawingImage

            return drawingImage, positives, falsepositives, negatives
            
            #self.img.texture = self.visionLib.opencv2kivyImage(drawingImage)
            strs = "Resultado de testes  OK >> " + str(len(self.positives)) + "    NG >> " + str(len(self.negatives)) + "   ** >> " + str(len(self.falsepositives))
            #toast( strs, background=(0,1,0,.7))   
        except Exception as ex:
            #toast("Falha ao tentar verificar resultados!", background=(1,0,0,.7))  
            #self.data_results.append({'active_icon': 'not-found-image.jpg', 'result': 'NG', 'text': str(time.time()), 'side': side, 'status_icon':'images/green.png' }) 
            return source, positives, falsepositives, negatives
            pass

    def train_product_model(self, model_file, _epochs, _imgsz, yaml):
        if(os.path.isfile(model_file)):
            model = YOLO(model_file)
        else: model = YOLO(model=yaml)

        results = model.train(data=yaml, epochs=_epochs, imgsz=_imgsz)

        pass

    def inference_product(self, model_source, image_inference):
        try:
            tstart = time.time()
            img = image_inference #cv2.imread(image_inference)

        
            model = YOLO(model_source)
            tmodel = time.time()


            #classNames = ['CE-MEDIUM0', 'CE-MEDIUM270', 'CE-SMALL0', 'CE-SMALL270', 'FID-CROSS', 'HDMI90', 'MIC90', 'RJ45', 'TYPE_C', 'USB270', 'USB90', 'VGA90']

            #images = [img, img]
            results = model.predict(img)
            tinference = time.time()
        
            #self.draw_inference_results(img, results, classNames)
            tdraw = time.time() 

        except:
            return None, 0, 0, 0


        gc.collect()

        #cv2.imshow("Results", img)
        #cv2.waitKey(0)

        return results, tmodel-tstart, "{:.2f}".format(tinference-tmodel), time.time()-tstart
    


    def train_models(self, model_source, yaml_file, epochs, isize):
        try:
            ultra = checks()
            tstart = time.time()

            model = YOLO(model_source)
            tmodel = time.time()


            #images = [img, img]
            results = model.train(data=yaml_file, epochs=int(epochs), imgsz=int(isize), device=0, batch=2)
            ttrain = time.time()
        
            #self.draw_inference_results(img, results, classNames)
            tdraw = time.time() 

        except Exception as ex:
            return None, 0, 0, 0


        gc.collect()

        #cv2.imshow("Results", img)
        #cv2.waitKey(0)

        return results, tmodel-tstart, "{:.2f}".format(ttrain-tmodel), time.time()-tstart



    def create_synth_fiducial(self, fiducialInnerDiameterInPixels, fiducialOuterDiameterInPixels):
        # Create a synthetic fiducial image
        pattern_sizeHW = [fiducialOuterDiameterInPixels, fiducialOuterDiameterInPixels]
        if fiducialOuterDiameterInPixels %2 == 0:  # Make sure the pattern size is odd
            pattern_sizeHW[0] += 1
            pattern_sizeHW[1] += 1
        fiducial_pattern = np.zeros(pattern_sizeHW, dtype=np.uint8)
        cv2.circle(fiducial_pattern, (pattern_sizeHW[1]//2, pattern_sizeHW[0]//2), fiducialOuterDiameterInPixels//2, 70, cv2.FILLED)  # The outer disk is dark gray
        cv2.circle(fiducial_pattern, (pattern_sizeHW[1]//2, pattern_sizeHW[0]//2), fiducialInnerDiameterInPixels//2, 255, cv2.FILLED)  # The inner disk is white
        # Standardize the pattern image
        standardized_fiducial_pattern = (fiducial_pattern.astype(np.float32) - fiducial_pattern.mean())/fiducial_pattern.std()

    
    #def fid_matchTemplate(self):
    #    # Pattern match
    #    match_img = cv2.matchTemplate(grayscale_img.astype(np.float32), standardized_fiducial_pattern, cv2.TM_CCOEFF_NORMED)
    #    # Create an 8-bit version of the match image for visualization, padded with zeros to get an image the same size as the original
    #    padded_match_8bits_img = np.zeros((img_shapeHWC[0], img_shapeHWC[1]), dtype=np.uint8)
    #    padded_match_8bits_img[fiducial_pattern.shape[0]//2: fiducial_pattern.shape[0]//2 + match_img.shape[0],
    #        fiducial_pattern.shape[1]//2: fiducial_pattern.shape[1]//2 + match_img.shape[1]] = (128 * (match_img + 1.0)).astype(np.uint8)



    def Locate_Object(self, _img, ref_path):
        min_match = 10

        #greyscale image
        ref = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE)

        if _img.ndim > 2:
            _img = cv2.cvtColor(_img, cv2.COLOR_BGR2GRAY)


        orb = cv2.ORB_create()

        kp1, des1 = orb.detectAndCompute(_img, None)
        kp2, des2 = orb.detectAndCompute(ref, None)

        # create BFMatcher object
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Match descriptors.
        matches = bf.match(des1,des2)
        # Sort them in the order of their distance.
        matches = sorted(matches, key = lambda x:x.distance)
        
    
        if len(matches)>10:
            dst_pts = np.float32([ kp1[m.queryIdx].pt for m in matches ]).reshape(-1,1,2)
            src_pts = np.float32([ kp2[m.trainIdx].pt for m in matches ]).reshape(-1,1,2)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
            matchesMask = mask.ravel().tolist()
            h,w = ref.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)
            #_img = cv2.polylines(_img,[np.int32(dst)],True,255,3, cv2.LINE_AA)

            return pts, M
        else:
            print( "Not enough matches are found - {}/{}".format(len(matches), 10) )
            matchesMask = None

        
        # Draw first 10 matches.
        #img3 = cv2.drawMatches(_img,kp1,ref,kp2,matches[:10],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        #plt.imshow(img3),plt.show()
   
    def pts_homography(self, pts, M):
        dst = cv2.perspectiveTransform(pts,M)

        return dst

