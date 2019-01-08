import cv2
from moviepy.editor import VideoFileClip
import Main

if __name__ == "__main__":
    
    cap = cv2.VideoCapture("VIDEO3.avi")
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = 0
    clip = VideoFileClip("VIDEO3.avi")
    
    while (n != length):
        
        ret, frame = cap.read()

            #small = cv2.resize(frame, (0, 0), fx = 0.25, fy = 0.25)
            #rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame1 = frame[100:]
            #frame2 = frame[400:600, 750:1900]
            #cv2.waitKey(0)
        result = str(Main.main(frame1))
        if len(result) != 0:
            print("Found plate: " + result + "\n")

        cv2.imshow('Video', frame1)
            #Main.main(frame2)

        n += 1

    print("Finished.")
    cap.release()
