import cv2
from moviepy.editor import VideoFileClip
import Main
import requests
from utils.color_recognition_module import color_recognition_api
import numpy as np

class roiLine:
    #pixel pos, real position, and width of line in pixels
    def __init__(self, pos, real_pos, width = 20):
        self.pos = pos
        self.real_pos = real_pos
        self.last_passed = {}
        self.width = width
        self.line_counter = False
   
    def is_passing(self, cy, cx):
        if(self.pos + self.width >= cy and self.pos - self.width <= cy):
            self.line_counter = True
            if not ((cy / cx) in self.last_passed):
                self.last_passed[(cy / cx)] = (time.time(), cx) #use license number detection instead of this
            return True
        return False

    def draw_line(self, frame):
        if self.line_counter:
            cv2.line(frame, (0, self.pos), (len(frame[0]), self.pos), (0, 0xFF, 0), 5)
        else:
            cv2.line(frame, (0, self.pos), (len(frame[0]), self.pos), (0, 0, 0xFF), 5)

if __name__ == "__main__":
    
    cap = cv2.VideoCapture("VIDEO4.avi")
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = 0
    clip = VideoFileClip("VIDEO4.avi")
    previous = ""

    w = cap.get(3)
    h = cap.get(4)
    frameArea = h * w
    areaTH = frameArea / 400

    fline = roiLine(150, 0)
    sline = roiLine(250, 5)

    #Background Subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows = True)

    #Kernals
    kernalOp = np.ones((3,3), np.uint8)
    kernalOp2 = np.ones((5,5), np.uint8)
    kernalCl = np.ones((11,11), np.int)
    
    crop_vehicle = None
   
    while (n != length):

        ret, frame = cap.read()

        fgmask = fgbg.apply(frame)
        fgmask2 = fgbg.apply(frame)

        #Binarization
        ret,imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        ret,imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)

        #OPening i.e First Erode the dilate
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernalOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_CLOSE, kernalOp)

        #Closing i.e First Dilate then Erode
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernalCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernalCl)

        fline.line_counter = False
        sline.line_counter = False

        #Find Contours
        _, countours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        for cnt in countours0:
            area = cv2.contourArea(cnt)
            #print(area)
            #print(cnt)
            
            if area > areaTH + 10000:
                ####Tracking######
                m = cv2.moments(cnt)
                cx = int(m['m10'] / m['m00'])
                cy = int(m['m01'] / m['m00'])
                x, y, w, h = cv2.boundingRect(cnt)
                crop_vehicle = frame[y:y + h, x:x + w]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                result, plateCoordinates = Main.main(crop_vehicle)
                if result != "":

                    print("License Plate: " + str(result) + "\n")

                    color = color_recognition_api.color_recognition(frame[int(plateCoordinates[2][1] - 150) : int(plateCoordinates[0][1] - 100), int(plateCoordinates[1][0]) : int(plateCoordinates[3][0])])
                    print("Color: " + str(color) + "\n")
                    print("-----------------------------------------------------------------\n")
                    
                    if previous != result:
                        print("Send...\n")
                        r = requests.post("https://fathomless-plains-27484.herokuapp.com/api/v1/s3M5aCMtypyas8fs1VPHhw/passages", data = {'car_num': result, 'color': color, 'camera_id': 1})
                        print(r.status_code, r.reason)
                        previous = result
                    else:
                        print("Repeated. Not sent.")
                    cv2.imshow("Warped", frame[int(plateCoordinates[2][1] - 200) : int(plateCoordinates[0][1] - 100), int(plateCoordinates[1][0]) : int(plateCoordinates[3][0])])

        cv2.imshow('Video', frame)
            #Main.main(frame2)

        if cv2.waitKey(1)&0xff==ord('q'):
            break

        n += 1

    print("Finished.")
    cap.release()
