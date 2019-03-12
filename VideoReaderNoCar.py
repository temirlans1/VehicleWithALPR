import cv2
from moviepy.editor import VideoFileClip
import Main
import requests
from utils.color_recognition_module import color_recognition_api
import numpy as np
import json

with open('./config.json') as f:
    config = json.load(f)

ip = str(config["ip"])

if __name__ == "__main__":
    
    cap = cv2.VideoCapture(ip)
    n = 0
    previous = ""
   
    while True:

        ret, frame = cap.read()

        """if n % 5 == 0:

            result, plateCoordinates = Main.main(frame[50:])

            if result != "":

                print("License Plate: " + str(result) + "\n")

                color = color_recognition_api.color_recognition(frame[int(plateCoordinates[2][1] - 150) : int(plateCoordinates[0][1] - 100), int(plateCoordinates[1][0]) : int(plateCoordinates[3][0])])
                print("Color: " + str(color) + "\n")
                print("-----------------------------------------------------------------\n")
                
                if previous != result:
                    print("Send...\n")
                    r = requests.post("https://fathomless-plains-27484.herokuapp.com/api/v1/s3M5aCMtypyas8fs1VPHhw/passage", data = {'car_num': result, 'color': color, 'camera_id': 1})
                    print(r.status_code, r.reason)
                    previous = result
                else:
                    print("Repeated. Not sent.")
                
                #cv2.imshow("Warped", frame[int(plateCoordinates[2][1] - 200) : int(plateCoordinates[0][1] - 100), int(plateCoordinates[1][0]) : int(plateCoordinates[3][0])])"""

        cv2.imshow('Video', frame)
            #Main.main(frame2)

        if cv2.waitKey(1)&0xff==ord('q'):
            break

        n += 1

    print("Finished.")
    cap.release()
