import cv2
import vehicles
import numpy as np
from random import randint
from vehicles import Car

if __name__ == "__main__":
    
    cap = cv2.VideoCapture("Highway1.mp4")
    car_cascade = cv2.CascadeClassifier('cars.xml')
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = 0
    pid = 0
    cars = []
    allCars = set([])
    frameCount = 0

    while (n != length):
    
        ret, frame = cap.read()
        frameCount += 1
        x1, y1 = 639, 178
        x2, y2 = 451, 719
        lineThickness = 2
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        x3, y3 = 727, 187
        x4, y4 = 790, 719
        lineThickness = 2
        cv2.line(frame, (x3, y3), (x4, y4), (0, 0, 255), 2)     

        gray = cv2.cvtColor(frame[180:], cv2.COLOR_BGR2GRAY)

        objects = car_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in objects:
            y += 180
            found = False
            cx, cy = x + w / 2, y + h / 2
            if len(cars) == 0:
                newCar = Car(pid, cx, cy, frameCount)
                cars.append(newCar)
                allCars.add(newCar)
                pid += 1
                continue
            for i in cars:
                if abs(cx - i.getCX()) <= 30 and abs(cy - i.getCY()) <= 30:
                    found = True
                    i.updateCoords(cx, cy)
                    i.updateFrameCount(frameCount)
                    allCars.add(i)
                    break
            if not found:
                newCar = Car(pid, cx, cy, frameCount)
                cars.append(newCar)
                allCars.add(newCar)
                pid += 1
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cars = [x for x in cars if not (frameCount - x.getFrameCount()) > 10]  

        for i in cars:
            cv2.putText(frame, str(i.getID()), (int(i.getCX()), int(i.getCY())), cv2.FONT_HERSHEY_SIMPLEX, 1, (randint(0, 255), randint(0, 255), randint(0, 255)), 1, cv2.LINE_AA)
                
        cv2.imshow("Frame", frame)
        
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    
        n += 1

    for i in allCars.copy():
        i.calculateFluctuations()
        if i.getFluctuations() == 0:
            allCars.discard(i)
            continue
    
    for i in sorted(allCars, key = Car.getFluctuations):
        print(i)   

    print("Finished.")
    cap.release()
    cv2.destroyAllWindows()
