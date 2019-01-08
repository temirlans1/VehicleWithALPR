import cv2
import Main

cap = cv2.VideoCapture(0)

while True:

    ret, frame = cap.read()
    
    #frame1 = frame[100:]
    #small = cv2.resize(frame, (0, 0), fx = 0.25, fy = 0.25)
    #rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    #frame2 = frame[400:600, 750:1900]
    #cv2.waitKey(0)

    found_car_frame, result = ALPRon(frame)

    if len(found_car_frame) == 0 and len(result) == 0:
        continue
    else:
        #Call the method to access database with arguments of frame, license plate number and POST request
    
print("Finished.")
cap.release()

def ALPRon(frame):

    result = str(Main.main(frame))

    if len(result) != 0:
        return frame, result
    else:
        return [], []
