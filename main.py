import cv2
import numpy as np
import vehicles
import time
import imutils
import PlateDetection as licPlateDetect

import Main
from utils.color_recognition_module import color_recognition_api

cnt_up=0
cnt_down=0


cap=cv2.VideoCapture("videos/VIDEO3.avi")

#Get width and height of video

w=cap.get(3)
h=cap.get(4)
frameArea=h*w
areaTH=frameArea/400

#Lines
line_up=int(2*(h/5))
line_down=int(3*(h/5))

up_limit=int(1*(h/5))
down_limit=int(4*(h/5))

print("Red line y:",str(line_down))
print("Blue line y:",str(line_up))
line_down_color=(255,0,0)
line_up_color=(255,0,255)
pt1 =  [0, line_down]
pt2 =  [w, line_down]
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up]
pt4 =  [w, line_up]
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit]
pt6 =  [w, up_limit]
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit]
pt8 =  [w, down_limit]
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Background Subtractor
fgbg=cv2.createBackgroundSubtractorMOG2(detectShadows=True)

#Kernals
kernalOp = np.ones((3,3),np.uint8)
kernalOp2 = np.ones((5,5),np.uint8)
kernalCl = np.ones((11,11),np.int)


font = cv2.FONT_HERSHEY_SIMPLEX
cars = []
max_p_age = 4
pid = 1

#Control lines

last_computed = (-1,-1)
x_const = 20
xs_const = 50
speed_lim = 60
fps = cap.get(cv2.CAP_PROP_FPS)
frame_num = 0
class roiLine:
    #pixel pos, real position, and width of line in pixels
    def __init__(self, pos, real_pos, width = 20):
        
        self.pos = pos
        self.real_pos = real_pos
        self.last_passed = {}
        self.width = width
        self.line_counter = False
   
    def is_passing(self, cy, cx):
        if( self.pos + self.width >= cy and self.pos - self.width <= cy):
            self.line_counter = True
            if not ((cy / cx) in self.last_passed):
                self.last_passed[ (cy / cx) ] = (time.time(), cx) #use license number detection instead of this
            return True
        return False

    def draw_line(self, frame):
        if self.line_counter:
            cv2.line(frame, (0, self.pos), (len(frame[0]), self.pos), (0, 0xFF, 0), 5)
        else:
            cv2.line(frame, (0, self.pos), (len(frame[0]), self.pos), (0, 0, 0xFF), 5)


fline = roiLine(150, 0)
sline = roiLine(250, 5)
fps = cap.get(cv2.CAP_PROP_FPS)
color = "unknown"
licPlate = "unknown"
wait = 1 / fps
while(cap.isOpened()):
    time.sleep(wait)
    ret,frame=cap.read()
    if frame is None:
        break
    height, width, layers = frame.shape
    new_h = height // 2
    new_w = width // 2
    frame = cv2.resize(frame, (new_w, new_h))
    frame_num += 1
    #transpose(image, image)
    #frame = imutils.rotate(frame, -90)
    for i in cars:
        i.age_one()
    fgmask=fgbg.apply(frame)
    fgmask2=fgbg.apply(frame)

    if ret==True:

        #Binarization
        ret,imBin=cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
        ret,imBin2=cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
        #OPening i.e First Erode the dilate
        mask=cv2.morphologyEx(imBin,cv2.MORPH_OPEN,kernalOp)
        mask2=cv2.morphologyEx(imBin2,cv2.MORPH_CLOSE,kernalOp)

        #Closing i.e First Dilate then Erode
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernalCl)
        mask2=cv2.morphologyEx(mask2,cv2.MORPH_CLOSE,kernalCl)

        fline.line_counter = False
        sline.line_counter = False

        #Find Contours
        _, countours0,hierarchy=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in countours0:
            area=cv2.contourArea(cnt)
            #print(area)
            #print(cnt)
            
            if area>areaTH+10000:
                ####Tracking######
                m=cv2.moments(cnt)
                cx=int(m['m10']/m['m00'])
                cy=int(m['m01']/m['m00'])
                x,y,w,h=cv2.boundingRect(cnt)
                crop_vehicle = frame[y + int(h/2):y+h, x:x+w]
                #cv2.imwrite("secondPass.jpg", crop_vehicle)
                licPlate = Main.main(crop_vehicle)
                if(licPlate != ""):
                    file = open("plates.txt", "a")
                    file.write(licPlate + "\n")
                    file.close()
                #print(Main.main(crop_vehicle))
                #print(str(x) + " " + str(y) + " " + str(w) + " " + str(h))
                new=True
                """if cy in range(up_limit,down_limit):
                    for i in cars:
                        if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                            new = False
                            i.updateCoords(cx, cy)

                            if i.going_UP(line_down,line_up)==True:
                                cnt_up+=1
                                print("ID:",i.getId(),'crossed going up at', time.strftime("%c"))
                            elif i.going_DOWN(line_down,line_up)==True:
                                cnt_down+=1
                                print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                            break
                        if i.getState()=='1':
                            if i.getDir()=='down'and i.getY()>down_limit:
                                i.setDone()
                            elif i.getDir()=='up'and i.getY()<up_limit:
                                i.setDone()
                        if i.timedOut():
                            index=cars.index(i)
                            cars.pop(index)
                            del i

                    if new==True: #If nothing is detected,create new
                        p=vehicles.Car(pid,cx,cy,max_p_age)
                        cars.append(p)
                        pid+=1
"""
                #cv2.circle(frame,(cx,cy),5,(0,0,255),-1)
                #img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                if( fline.is_passing(cy, cx)):
                    crop_vehicle = frame[y:y+h, x:x+w]
                    color = color_recognition_api.color_recognition(crop_vehicle)
                    cv2.imwrite("firstPass.jpg", crop_vehicle)
                    #cv2.imshow("cropped_first", crop_vehicle)
                
                if( sline.is_passing(cy, cx)):
                    crop_vehicle = frame[y + int(h/2):y+h, x:x+w]
                    #color = color_recognition_api.color_recognition(crop_vehicle)
                    #cv2.imshow("cropped_second", crop_vehicle)
                    cv2.imwrite("secondPass.jpg", crop_vehicle)
                    """licPlate = Main.main(crop_vehicle)
                    if(licPlate != ""):
                        cv2.imwrite("detected.jpg", crop_vehicle)"""
                    
                key_to_del = None
                key2_to_del = None
                for key, value in fline.last_passed.items():
                    for skey, svalue in sline.last_passed.items():
                        if(abs(skey - key) < 2):
                            key_to_del = key
                            key2_to_del = skey
                            speed = (sline.real_pos - fline.real_pos) / (svalue[0] - value[0])
                            speed *= 3.6 # converting to km/h
                            if(speed > speed_lim):
                                file = open("speed_violations.txt", "a")
                                file.write("{} - {} - {} km/h\n".format(svalue[1], value, speed))
                                file.close()
                            last_computed = (svalue[1], speed)
                        
                        
                
                if key_to_del != None:
                    del fline.last_passed[key_to_del]
                if key2_to_del != None:
                    del sline.last_passed[key2_to_del]

                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                #print(cy)
            if(last_computed[0] != -1 and speed > 0):
                #print(licPlate)
                cv2.putText(
                        frame,
                        str(licPlate) + color + ' || Speed: ' + str(last_computed[1]),
                        (last_computed[0]-200, 100),
                        font,
                        0.5,
                        (0xFF, 0xFF, 0xFF),
                        1,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        )    
            
        fline.draw_line(frame)
        sline.draw_line(frame)
            
            #for i in cars:
            #    cv2.putText(frame, str(i.getId()), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)




        #str_up='UP: '+str(cnt_up)
        #str_down='DOWN: '+str(cnt_down)
        #frame=cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
        #frame=cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
        #frame=cv2.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
        #frame=cv2.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
        #cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        #cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        #cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        #cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        #cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('Frame', 1000,1000)
        cv2.imshow('Frame',frame)

        if cv2.waitKey(1)&0xff==ord('q'):
            break

    else:
        break

cap.release()
cv2.destroyAllWindows()








