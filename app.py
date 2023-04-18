from sqlalchemy.sql import text as sql_text
from sqlalchemy.sql import insert
import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Teacher, Student, student_dropoff, Pickup


# Add necessary imports from RFID code
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trm51'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://phpmyadmin:password@192.168.1.2/RCSS'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(email):
    print("Loading user with email:", email)
    
    admin = Admin.query.filter_by(email=email).first()
    if admin:
        return admin

    teacher = Teacher.query.filter_by(email=email).first()
    if teacher:
        print("Teacher email: " + email)
        return teacher

    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print(f"Email: {email}, Password: {password}")

        admin = Admin.query.filter_by(email=email).first()
        teacher = Teacher.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            print("Admin email: {}".format(teacher))
            password_match = check_password_hash(admin.password, password)
            print(f"Password match: {password_match}")
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        elif teacher and check_password_hash(teacher.password, password):
            print("Teacher email: {}".format(teacher))
            password_match = check_password_hash(teacher.password, password)
            print(f"Password match: {password_match}")
            login_user(teacher)
            return redirect(url_for('teacher_dashboard'))
        else:
            flash("Error: Intente de nuevo")

    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    dropoffs =student_dropoff.query.all()
    pickups = Pickup.query.all()
    students = Student.query.all()
    teachers = Teacher.query.all()
    return render_template('admin_dashboard.html', dropoffs=dropoffs, pickups=pickups, students=students, teachers=teachers)

@app.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if not isinstance(current_user, Teacher):
        flash("Error: Access denied")
        return redirect(url_for('login'))
        
    teacher = current_user
    students = Student.query.filter_by(teacher_name=teacher.first_name + ' ' + teacher.last_name).all()
    student_ids = [student.student_id for student in students]
    dropoffs = student_dropoff.query.filter(student_dropoff.student_id_fk.in_(student_ids)).all()
    pickups = Pickup.query.filter(Pickup.student_name.in_(student_ids)).all()
    return render_template('teacher_dashboard.html', students=students, dropoffs=dropoffs, pickups=pickups)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

import threading
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time


def rfid_function():
    # Set up the LED pins
    green_led_pin = 17
    red_led_pin = 27

    # Initialize the GPIO library
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(green_led_pin, GPIO.OUT)
    GPIO.setup(red_led_pin, GPIO.OUT)

    # Function to turn LEDs on or off
    def set_leds(green, red):
        GPIO.output(green_led_pin, green)
        GPIO.output(red_led_pin, red)
    
    def blink_leds_no_match (times, delay):
        for _ in range(times):
            set_leds(True, True)
            time.sleep(delay)
            set_leds(False, False)
            time.sleep(delay)
    def blink_leds_success (times, delay):
        for _ in range(times):
            set_leds(True, False)
            time.sleep(delay)

    reader = SimpleMFRC522()

    last_swiped_id = None
    last_swipe_time = None
    try:
        while True:
            # (The rest of the reading loop code remains the same.)
            set_leds(False, True)  # Turn the red LED on and the green LED off while waiting for a tag
            id_number, text = reader.read()
            time.sleep(0.5)
            set_leds(True, False)  # Turn the green LED on and the red LED off when a tag is read

            # Check if the RFID id_number matches any student id
            with app.app_context():
                with db.engine.connect() as connection:
                    result = connection.execute(sql_text("SELECT student_id, first_name, last_name FROM students WHERE student_id = :id"), {'id': str(id_number)})
                    record = result.fetchone()
                    if record:
                        student_id, first_name, last_name =record
                        student_name = f"{first_name} {last_name}"
                    else:
                        print("No ID match found")
                        student_id = None

                    if student_id:
                        current_time = datetime.datetime.now()

                        # Check if the last_swiped_id is the same as the current one and if the time difference is less than 10 seconds
                        if last_swiped_id == id_number and (current_time - last_swipe_time).total_seconds() < 5:
                            print("Swipe blocked for ID", id_number)
                            continue

                        last_swiped_id = id_number
                        last_swipe_time = current_time

                        # Check if there's a dropoff entry for the student with today's date
                        today = datetime.date.today()
                        result = connection.execute(sql_text("SELECT * FROM student_dropoff WHERE student_id_fk = :id AND DATE(dropoff_time) = :today"), {'id': student_id, 'today': today})
                        dropoff_entry = result.fetchone()

                        if not dropoff_entry:
                            # Insert the matched student id into the dropoff table
                            stmt = "INSERT INTO student_dropoff (student_id_fk, student_name, dropoff_time) VALUES (:id, :student_name, :dropoff_time)"
                            params = {"id": student_id, "student_name": student_name, "dropoff_time": datetime.datetime.now()}
                            connection.execute(sql_text(stmt), params)
                            connection.commit()  # Commit the transaction
                            print("Dropoff info inserted")
                            blink_leds_success(1,0.5)

                        else:
                           # Check if there's a pickup entry for the student with today's date
                            result = connection.execute(sql_text("SELECT * FROM student_pickup WHERE student_name = :student_name AND DATE(pickup_time) = :today"), {'student_name': student_name, 'today': today})
                            pickup_entry = result.fetchone()

                            # If there is no pickup entry or it has been more than 10 minutes since the last swipe, insert a pickup entry
                            pickup_time_index = list(result.keys()).index('pickup_time')
                            if not pickup_entry:
                                print("No pickup entry found")
                                last_swipe_time = current_time
                            elif (current_time - pickup_entry[pickup_time_index]).total_seconds() >= 10:
                                print("More than 10 minutes since the last swipe")
                                last_swipe_time = current_time
                            else:
                                print("Time since last swipe:", (current_time - pickup_entry[pickup_time_index]).total_seconds())

                            if not pickup_entry or (current_time - pickup_entry[pickup_time_index]).total_seconds() >= 10:
                                stmt = "INSERT INTO student_pickup (student_name, pickup_time) VALUES (:student_name, :pickup_time)"
                                params = {"student_name": student_name, "pickup_time": datetime.datetime.now()}
                                connection.execute(sql_text(stmt), params)
                                connection.commit()  
                                print("Pickup info inserted")
                                blink_leds_success(1,0.5)
                            else:
                                print("Swipe blocked for ID", id_number)
                                for i in range(3):
                                    set_leds(False, True)
                                    time.sleep(.25)
                                    set_leds(False, False)
                                    time.sleep(.25)


                    else:
                        print("No ID match found")
                        blink_leds_no_match(3, 0.5)

    finally:
        set_leds(False, False)  # Turn both LEDs off before exiting
        GPIO.cleanup()

# Call the rfid_function in a separate thread when the application starts
rfid_thread = threading.Thread(target=rfid_function)
rfid_thread.start()



if __name__ == '__main__':
    app.run(debug=True)
