import os
import pickle
import cv2
import face_recognition
import cvzone
import mysql.connector
from datetime import datetime
import numpy as np

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="12345678",  
    database="FaceAttendance"
)
cursor = db_connection.cursor()

print("Loading Encode File ...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = int(np.argmin(faceDis))

            if matches[matchIndex]:
                student_id = studentIds[matchIndex]
                print(f"Match Found: {student_id}")

 
                cursor.execute("SELECT * FROM EntryLog WHERE student_id = %s AND DATE(entry_time) = CURDATE()", (student_id,))
                entry_record = cursor.fetchone()

                if not entry_record:
                  
                    name = f"Student {student_id}" 
                    entry_time = datetime.now()
                    cursor.execute(
                        "INSERT INTO EntryLog (student_id, name, entry_time) VALUES (%s, %s, %s)",
                        (student_id, name, entry_time)
                    )
                    db_connection.commit()
                    print(f"Entry logged for {student_id} at {entry_time}")

                else:
   
                    cursor.execute("SELECT * FROM ExitLog WHERE student_id = %s AND DATE(exit_time) = CURDATE()", (student_id,))
                    exit_record = cursor.fetchone()

                    if not exit_record:
                      
                        name = f"Student {student_id}"  
                        exit_time = datetime.now()
                        cursor.execute(
                            "INSERT INTO ExitLog (student_id, name, exit_time) VALUES (%s, %s, %s)",
                            (student_id, name, exit_time)
                        )
                        db_connection.commit()
                        print(f"Exit logged for {student_id} at {exit_time}")

    cv2.imshow("Face Attendance", img)
    cv2.waitKey(1)
