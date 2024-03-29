import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://attendance-system-1bc90-default-rtdb.firebaseio.com/", 
    'storageBucket' : "attendance-system-1bc90.appspot.com"
})

folderPathImages = "Images"
listPathImages = os.listdir(folderPathImages)
imgListImages = []

# Extracting Student iDS
studentIDs = []

for path in listPathImages:
    imgListImages.append(cv2.imread(os.path.join(folderPathImages,path)))
    # Taking only the first element after splitting text and storing
    # that into student IDs
    studentIDs.append(os.path.splitext(path)[0])

    # This loop will be used to store the images
    # Join together the full filename using folderPathImages as well as each individual path
    fileName = f'{folderPathImages}/{path}'
    # The following code will retrieve a reference to your established cloud storage
    bucket = storage.bucket()
    # A reference to a specific object is created
    blob = bucket.blob(fileName)
    # The file with the filename is uploaded to the reference 'blob' created in your cloud storage
    blob.upload_from_filename(fileName)

def generateEncodings(images):
    encodingsList = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingsList.append(encode)

    return encodingsList

encodingsListKnown = generateEncodings(imgListImages)
encodingsListWithIDs = [encodingsListKnown, studentIDs]

# Opening a new file called EncodingsFile.p in WRITE MODE
encodingFile = open("EncodingsFile.p", "wb")
# Using pickle to dump into the file your encodings list
pickle.dump(encodingsListWithIDs, encodingFile)
# Closing the file
encodingFile.close()