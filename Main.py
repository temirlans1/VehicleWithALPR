import cv2
import numpy as np
import os

import DetectChars
import DetectPlates
import PossiblePlate

import pytesseract
from PIL import Image

# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
config = ('-l eng --oem 3 --psm 6')

showSteps = False

###################################################################################################
def main(frame):

    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()         # attempt KNN training

    if blnKNNTrainingSuccessful == False:                               # if KNN training was not successful
        print("\nERROR: KNN traning was not successful!\n")  # show error message
        return ""                                                # and exit program
    # end if

    imgOriginalScene = frame

    if imgOriginalScene is None:                            # if image was not read successfully
        print("\nERROR: image not read from file!\n\n")  # print error message to std out
        return ""                                              # and exit program
    # end if

    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates

    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        print("\nNO license plates were detected!\n")  # inform user no plates were found
        return ""
    else:
        #cv2.imwrite("detected.jpg", frame)                                                       # else
                # if we get in here list of possible plates has at leat one plate

                # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)

                # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
        licPlate = listOfPossiblePlates[0]

#----------------------------------------------------------------------------------------------

        img = cv2.cvtColor(licPlate.imgPlate, cv2.COLOR_BGR2GRAY)

        # Apply dilation and erosion to remove some noise
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations = 1)
        img = cv2.erode(img, kernel, iterations = 1)

        result = pytesseract.image_to_string(img)

        result.replace(" ", "")

        filtered_result = ""
    
        for i in result:
                if (ord(i) >= 48 and ord(i) <= 57) or (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                        filtered_result += i

        j = 0

        for i in filtered_result:
            if j == 0 or j == 1 or j == 2 or j == 3:
                if (ord(i) >= 48 and ord(i) <= 57):
                    j += 1
        
        if j == 4:
            filtered_result = filtered_result[1:]

        j = 0
        
        for i in filtered_result:
            if j == 4 or j == 5 or j == 6 or j == 7:
                if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                    j += 1

        if j == 4:
            filtered_result = filtered_result[:6] + filtered_result[7:]

#----------------------------------------------------------------------------------------------

        tesseract = str(pytesseract.image_to_string(licPlate.imgThresh, config = config))

        enlargedImg3 = cv2.resize(licPlate.imgPlate, (0, 0), fy = 1.6, fx = 1.6)
        tesseractEnlarged3 = str(pytesseract.image_to_string(enlargedImg3, config = config))
        tesseractEnlarged3.replace(" ", "")

        if len(tesseractEnlarged3) > 8:
            tesseractEnlarged3 = tesseractEnlarged3[1:]
            tesseractEnlarged3 = tesseractEnlarged3[:6] + tesseractEnlarged3[7:]

        enlargedImg4 = cv2.resize(licPlate.imgPlate, (0, 0), fy = 2, fx = 2)
        tesseractEnlarged4 = str(pytesseract.image_to_string(enlargedImg4, config = config))
        tesseractEnlarged4.replace(" ", "")

        if len(tesseractEnlarged4) > 8:
            tesseractEnlarged4 = tesseractEnlarged4[1:]
            tesseractEnlarged4 = tesseractEnlarged4[:6] + tesseractEnlarged4[7:]
            tesseractEnlarged4 = tesseractEnlarged4[:8]

        if len(licPlate.strChars) == 0:                     # if no chars were found in the plate
            print("\nNO characters were detected!\n\n")  # show message
            return ""                                          # and exit program
        # end if

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)             # draw red rectangle around plate

        filtered_tesseract = ""

        for i in tesseract:
                if (ord(i) >= 48 and ord(i) <= 57) or (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                        filtered_tesseract += i

        j = 0

        for i in licPlate.strChars:
            if j == 0 or j == 1 or j == 2 or j == 3:
                if (ord(i) >= 48 and ord(i) <= 57):
                    j += 1
        
        if j == 4:
            licPlate.strChars = licPlate.strChars[1:]

        j = 0
        
        for i in licPlate.strChars:
            if j == 4 or j == 5 or j == 6 or j == 7:
                if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                    j += 1

        if j == 4:
            licPlate.strChars = licPlate.strChars[:6] + licPlate.strChars[7:]

        j = 0
        k = 0
        finalResult = ""

        if len(filtered_tesseract) <= 3:
            filtered_tesseract = ""

        valid = True
        j = 0

        if len(filtered_result) != 7:
            valid = False

        for i in filtered_result:
            if j == 0 or j == 4 or j == 5 or j == 6:
                if not ((ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122)):
                    valid = False
                    break
            if j == 1 or j == 2 or j == 3:
                if not (ord(i) >= 48 and ord(i) <= 57):
                    valid = False
                    break
            j += 1
        
        if valid:
            licPlate.strChars = filtered_result
        else:

            valid = True
            j = 0
            finalResult = tesseractEnlarged3

            if len(finalResult) != 8:
                valid = False

            for i in finalResult:
                if j == 0 or j == 1 or j == 2 or j == 6 or j == 7:
                    if not (ord(i) >= 48 and ord(i) <= 57):
                        valid = False
                        break
                if j == 3 or j == 4 or j == 5:
                    if not((ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122)):
                        valid = False 
                        break  
                j += 1

            if valid:
                licPlate.strChars = finalResult
            else:

                valid = True
                j = 0
                finalResult = tesseractEnlarged4

                if len(finalResult) != 8:
                    valid = False

                for i in finalResult:
                    if j == 0 or j == 1 or j == 2 or j == 6 or j == 7:
                        if not (ord(i) >= 48 and ord(i) <= 57):
                            valid = False
                            break
                    if j == 3 or j == 4 or j == 5:
                        if not ((ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122)):
                            valid = False   
                            break
                    j += 1

                if valid:
                    licPlate.strChars = finalResult
                else:
                    
                    valid = True
                    j = 0
                    finalResult = ""
        
                    for i in tesseractEnlarged3:
                        if tesseractEnlarged4.find(i) != -1:
                            j += 1
                        if j == 1:
                            finalResult += i
                            j = 0

                    if len(finalResult) != 8:
                        valid = False

                    j = 0

                    for i in finalResult:
                        if j == 0 or j == 1 or j == 2 or j == 6 or j == 7:
                            if not (ord(i) >= 48 and ord(i) <= 57):
                                valid = False
                                break
                        if j == 3 or j == 4 or j == 5:
                            if not ((ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122)):
                                valid = False  
                                break 
                        j += 1

                    if valid:
                        licPlate.strChars = finalResult
                    else:
                        licPlate.strChars = ""
        
    if licPlate.strChars is None:
        licPlate.strChars = ""

    return licPlate.strChars.upper()
# end main

###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function

###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height

            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function


















