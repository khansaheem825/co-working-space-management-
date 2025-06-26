import mysql.connector
import cv2
import face_recognition
import pickle
import os

db = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="12345678", 
    database="FaceAttendance" 
)
cursor = db.cursor()

folderPath = 'Images'
if not os.path.exists(folderPath):
    os.makedirs(folderPath)
    print(f"Created folder: {folderPath}")
    
pathList = os.listdir(folderPath)
if not pathList:
    print("No images found in the folder. Please add images to the 'Images' folder.")
    exit()

print("Images found:", pathList)

imgList = []
studentIds = []


def saveImageToDB(student_id, image_path):
    """Save image to the database."""
    try:
        with open(image_path, 'rb') as file:
            binary_data = file.read()

    
        cursor.execute("SELECT id FROM Students WHERE id = %s", (student_id,))
        result = cursor.fetchone()

        if result:
         
            cursor.execute("""
                UPDATE Students SET image = %s WHERE id = %s
            """, (binary_data, student_id))
        else:
          
            cursor.execute("""
                INSERT INTO Students (id, image) VALUES (%s, %s)
            """, (student_id, binary_data))

        db.commit()
        print(f"Image for Student ID {student_id} saved to database.")
    except Exception as e:
        print(f"Error saving image for Student ID {student_id}: {e}")

for path in pathList:
    student_id = os.path.splitext(path)[0]  
    image_path = os.path.join(folderPath, path)
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Invalid image file: {path}")

        imgList.append(img)
        studentIds.append(student_id)
        saveImageToDB(student_id, image_path)
    except Exception as e:
        print(f"Skipping {path}: {e}")

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]  
            encodeList.append(encode)
        except Exception as e:
            print(f"Error encoding an image: {e}")
    return encodeList

print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding complete.")


try:
    with open("EncodeFile.p", 'wb') as file:
        pickle.dump(encodeListKnownWithIds, file)
    print("Encodings saved to EncodeFile.p!")
except Exception as e:
    print(f"Error saving encodings to file: {e}")


db.close()
