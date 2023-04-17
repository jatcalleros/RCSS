#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import mysql.connector

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

reader = SimpleMFRC522()

# Database connection
cnx = mysql.connector.connect(
    host="192.168.1.2",
    user="phpmyadmin", 
    password="password", 
    database="RCSS")

cursor = cnx.cursor()

try:
    while True:
        set_leds(False, True)  # Turn the red LED on and the green LED off while waiting for a tag
        id_number, text = reader.read()
        set_leds(True, False)  # Turn the green LED on and the red LED off when a tag is read

        print(id_number)
        print(text)

        # Check if the RFID id_number matches any student id
 
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (str(id_number),))
        student_id = cursor.fetchone()
        if student_id:
            student_id = student_id[0]  # Assign the first element of the tuple to student_id
            print("ID match found: ", student_id)
            set_leds(True, False)  # Turn the green LED on and the red LED off when a match is found
            time.sleep(1)

            # Insert the matched student id into the student_dropoff table
            cursor.execute("INSERT INTO student_dropoff (student_id_fk, dropoff_time) VALUES (%s, NOW())", (student_id,))
            cnx.commit()

        else:
            print("No ID match found")
            for _ in range(3):  # Blink both LEDs 3 times rapidly
                set_leds(True, True)
                time.sleep(0.3)
                set_leds(False, False)
                time.sleep(0.3)


finally:
    set_leds(False, False)  # Turn both LEDs off before exiting
    cursor.close()
    cnx.close()
    GPIO.cleanup()

