import os
import mysql.connector
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import random
import string
import subprocess

app = Flask(__name__)


db = mysql.connector.connect(
    host="localhost", user="root", password="12345678", database="FaceAttendance"
)
cursor = db.cursor()


UPLOAD_FOLDER = 'Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = "your_secret_key" 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def generate_student_id():
    return ''.join(random.choices(string.digits, k=6))  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_name = request.form['name']
        student_major = request.form['major']
        starting_year = request.form['starting_year']
        total_attendance = 0  
        standing = request.form['standing']
        year = request.form['year']
        
  
        student_id = generate_student_id()


        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{student_id}.jpg")


            file.save(file_path)

 
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()

      
            try:
                cursor.execute("""
                    INSERT INTO Students (id, name, major, starting_year, total_attendance, standing, year, image_path, image) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (student_id, student_name, student_major, starting_year, total_attendance, standing, year, file_path, image_data))
                db.commit()

       
                flash(f"Student {student_name} registered successfully with ID {student_id}!", "success")
                return redirect(url_for('registration_success', student_id=student_id))

            except Exception as e:
                db.rollback()
                flash(f"Error registering student: {e}", "danger")
                return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/registration_success/<student_id>')
def registration_success(student_id):
    return render_template('success.html', student_id=student_id)

@app.route('/')
def home():
    return render_template('home.html') 

@app.route('/run-encode', methods=['POST'])
def run_encode():
    try:
    
        subprocess.run(['python', 'encodegenerator.py'], check=True)

        flash("Encoding generation completed successfully!", "success")
        return redirect(url_for('home'))
    except subprocess.CalledProcessError as e:
      
        flash(f"Error running the encoding script: {e}", "danger")
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=8080)
