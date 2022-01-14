import time
from board import SCL, SDA
import busio
from controller import XboxOneController
from common import map


# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685


if __name__ == "__main__":
    i2c = busio.I2C(SCL, SDA)
    pca1 = PCA9685(i2c, address=0x40)
    pca1.frequency = 50
    pca2 = PCA9685(i2c, address=0x41)
    pca2.frequency = 50
    
    servo0 = servo.Servo(pca1.channels[1])
    servo1 = servo.Servo(pca1.channels[2])

    c = XboxOneController()

    while True:
        #time.sleep(0.1)
        lx = map(c.axis_states.get('lx'),0, 255,0,180)
        ly = map(c.axis_states.get('ly'),0, 255,0,180)
        servo0.angle = lx
        servo1.angle = ly
        print(lx, "  ", ly)
