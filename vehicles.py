class Car:

    def __init__(self, pid, cx, cy, frameCount):
        self.pid = pid
        self.cx = cx
        self.cy = cy
        self.frameCount = frameCount
        self.track = [[cx, cy]]

    def getID(self): #For the ID
        return self.pid

    def getCX(self):  #For x coordinate
        return self.cx

    def getCY(self):  #For y coordinate
        return self.cy
    
    def getFrameCount(self):
        return self.frameCount

    def getTrack(self):
        return self.track

    def updateCoords(self, cx, cy):
        self.track.append([cx, cy])
        self.cx = cx
        self.cy = cy

    def updateFrameCount(self, frameCount):
        self.frameCount = frameCount

    def __repr__(self):
        return "ID: {}, CX: {}, CY: {}, FrameCount: {}, Track: {}".format(self.pid, self.cx, self.cy, self.frameCount, self.track)
