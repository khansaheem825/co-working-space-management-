import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'Images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="12345678",
    database="FaceAttendance"
)
cursor = db.cursor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        student_major = request.form['major']
        starting_year = request.form['starting_year']
        total_attendance = request.form['total_attendance']
        standing = request.form['standing']
        year = request.form['year']

      
        if 'image' not in request.files:
            return "No file part", 400
        file = request.files['image']
        
        if file.filename == '':
            return "No selected file", 400
        
       
        if file and allowed_file(file.filename):
            filename = f"{student_id}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            return "Invalid file format", 400

       
        cursor.execute("""
            INSERT INTO Students (id, name, major, starting_year, total_attendance, standing, year, image_path) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (student_id, student_name, student_major, starting_year, total_attendance, standing, year, file_path))
        db.commit()

        return redirect(url_for('success'))

    return render_template('register.html')

@app.route('/success')
def success():
    return "Registration Successful!"

if __name__ == '__main__':
    app.run(debug=True)
