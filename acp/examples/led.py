import time
import RPi.GPIO as GPIO

pin = 17 

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
GPIO.output(pin, GPIO.HIGH)
time.sleep(10)
GPIO.output(pin, GPIO.LOW)
GPIO.cleanup()