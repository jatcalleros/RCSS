import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

def main():
    # Instantiate the RFID reader object
    reader = SimpleMFRC522()

    try:
        print("Place your card near the reader...")
        # Read the RFID card
        id, text = reader.read()
        print("Card ID:", id)
        print("Card Text:", text)
    except Exception as e:
        print("Error reading card:", e)
    finally:
        # Clean up GPIO to prevent warnings and errors
        GPIO.cleanup()

if __name__ == "__main__":
    main()

