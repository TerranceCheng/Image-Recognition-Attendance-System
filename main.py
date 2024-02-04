# Create image size = 216 x 216 

import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://attendance-system-1bc90-default-rtdb.firebaseio.com/", 
    'storageBucket' : "attendance-system-1bc90.appspot.com"
})

bucket = storage.bucket()

# If using webcam = 0, if using external cam = 1
capture = cv2.VideoCapture(0)
capture.set(3, 640)
capture.set(4, 480)
backgroundImg = cv2.imread('Resources/Background.png')

folderPathMode = "Resources/Modes"
listPathMode = os.listdir(folderPathMode)
imgListMode = []

for path in listPathMode:
    imgListMode.append(cv2.imread(os.path.join(folderPathMode, path)))

# Importing encodings
encodingsFile = open("EncodingsFile.p", "rb")
encodingsListWithIDs = pickle.load(encodingsFile)
encodingsFile.close()

encodingsListKnown, studentIDs = encodingsListWithIDs

# Create a new variable called modeType
modeType = 0
counter = 0
id = -1

while True:
    success, image = capture.read()

    # Onto the position of 162:162 + 480, 55:55 + 640, you are pasting
    # your webcam over the backgroundImg
    image = cv2.resize(image, (640, 480))
    backgroundImg[162:162 + 480, 55:55 + 640] = image
    backgroundImg[44:44 + 633, 808:808 + 414] = imgListMode[modeType]

    # Making each frame taken from your webcam 1/4 if its actual size
    smallImage = cv2.resize(image, (0, 0), None, 0.25, 0.25)
    # Converting the image to RGB color format
    smallImage = cv2.cvtColor(smallImage, cv2.COLOR_BGR2RGB)

    # FINDING the face in the current webcam frame
    faceCurrentFrame = face_recognition.face_locations(smallImage)
    # Encoding the face found in the image
    encodeCurrentFrame = face_recognition.face_encodings(smallImage, faceCurrentFrame)

    # Showing a window for your webcam
    # cv2.imshow("My Webcam", image)

    if faceCurrentFrame:

        for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
            matches = face_recognition.compare_faces(encodingsListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodingsListKnown, encodeFace)
            matchIndex = np.argmin(faceDistance)

            if matches[matchIndex]:
                print("Registered Student Detected")
                print(studentIDs[matchIndex])

                # creating four points to map as the "corners" of your face 
                y1, x2, y2, x1 = faceLocation
                # resizing it to the actual size of the webcam feed
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                # creating a box that has line that wrap around our face
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                # having the rectangle we draw follow our face around, rt=0 means you're not outlining the box
                backgroundImg = cvzone.cornerRect(backgroundImg, bbox, rt = 0)

                id = studentIDs[matchIndex]

                if counter == 0:
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Retrieving students information from the database
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Retrieving student's image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                studentImg = cv2.imdecode(array ,cv2.COLOR_BGRA2BGR)

                # Update attendance record and data

                datetimeObject = datetime.strptime(studentInfo['last_attendance_taken'], "%Y-%m-%d %H:%M:%S")
                timeInSecsElapsed = (datetime.now() - datetimeObject).total_seconds()

                if timeInSecsElapsed > 30:
                    
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1

                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_taken').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    modeType = 3
                    counter = 0
                    backgroundImg[44:44 + 633, 808:808 + 414] = imgListMode[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                backgroundImg[44:44 + 633, 808:808 + 414] = imgListMode[modeType]

                if counter < 10:
                    # Indent this properly
                    # All will execute while modeType = 1

                    cv2.putText(backgroundImg, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['grades']), (910, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    cv2.putText(backgroundImg, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                    # In order to center the name, calculation needs to be performed
                    (width, height), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_SIMPLEX, 1, 1)

                    # We are using a double // because that gets rid of trailing float numbers
                    center_offset = (414 - width)//2
                    cv2.putText(backgroundImg, str(studentInfo['name']), (808 + center_offset, 445),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 1)
                    
                    backgroundImg[175:175 + 216, 909:909 + 216] = studentImg

            counter += 1

            if counter > 20:
                
                counter = 0
                modeType = 0
                studentInfo = []
                studentImg = []
                backgroundImg[44:44 + 633, 808:808 + 414] = imgListMode[modeType]

    else:
        modeType = 0
        counter = 0

    # Showing the window for your backgroundImg
    cv2.imshow("Attendance System", backgroundImg)
    cv2.waitKey(1)