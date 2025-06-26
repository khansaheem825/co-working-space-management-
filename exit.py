import cv2
import face_recognition
import pickle
import numpy as np
import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="FaceAttendance"
)
cursor = db.cursor()

print("Loading encodings...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encodings loaded.")

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

  
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            student_id = studentIds[matchIndex]
            print(f"Student ID: {student_id}")

            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                SELECT entry_time, exit_time FROM Logs 
                WHERE id = %s 
                ORDER BY entry_time DESC LIMIT 1
            """, (student_id,))
            result = cursor.fetchone()

            if result and result[1] is None:
                
                cursor.execute("""
                    UPDATE Logs SET exit_time = %s 
                    WHERE id = %s AND entry_time = %s
                """, (timestamp, student_id, result[0]))
                db.commit()
                print(f"Exit logged for Student ID {student_id} at {timestamp}")

          
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{student_id} - Exit", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    cv2.imshow("Face Attendance - Exit", img)
    cv2.waitKey(1)
