import cv2
import numpy as np

if __name__ == "__main__":
    
    cap = cv2.VideoCapture("Highway1.mp4")
    car_cascade = cv2.CascadeClassifier('cars.xml')
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = 0
    
    while (n != length):
    
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        cars = car_cascade.detectMultiScale(gray, 1.1, 5) #1.1, 3

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)      

        x1, y1 = 639, 178
        x2, y2 = 451, 719
        lineThickness = 2
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        x3, y3 = 727, 187
        x4, y4 = 790, 719
        lineThickness = 2
        cv2.line(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)

        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    
        n += 1

    print("Finished.")
    cap.release()
    cv2.destroyAllWindows()
