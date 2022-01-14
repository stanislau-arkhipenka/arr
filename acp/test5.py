import time
from board import SCL, SDA
import busio
from controller import XboxOneController
from common import map


# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
import board
from adafruit_motor import servo as ada_servo
from acp.servo import Servo
from adafruit_pca9685 import PCA9685


class aaa:

    PCA_FREQ = 50 # Servo control freq

    def __init__(self) -> None:
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca1 = PCA9685(self.i2c, address=0x41)
        self.pca2 = PCA9685(self.i2c, address=0x40)
        self.pca1.frequency = self.PCA_FREQ
        self.pca2.frequency = self.PCA_FREQ

        self.coxa1_servo  = Servo(ada_servo.Servo(self.pca1.channels[0]))     #18 servos = Servo()
        self.femur1_servo = Servo(ada_servo.Servo(self.pca1.channels[1]), reverse=True)
        self.tibia1_servo = Servo(ada_servo.Servo(self.pca1.channels[2]), reverse=True)
        self.coxa2_servo  = Servo(ada_servo.Servo(self.pca1.channels[3]))
        self.femur2_servo = Servo(ada_servo.Servo(self.pca1.channels[4]), reverse=True)
        self.tibia2_servo = Servo(ada_servo.Servo(self.pca1.channels[5]), reverse=True)
        self.coxa3_servo  = Servo(ada_servo.Servo(self.pca1.channels[6]))
        self.femur3_servo = Servo(ada_servo.Servo(self.pca1.channels[7]), reverse=True)
        self.tibia3_servo = Servo(ada_servo.Servo(self.pca1.channels[8]), reverse=True)
        self.coxa4_servo  = Servo(ada_servo.Servo(self.pca2.channels[0]))
        self.femur4_servo = Servo(ada_servo.Servo(self.pca2.channels[1]))
        self.tibia4_servo = Servo(ada_servo.Servo(self.pca2.channels[2]))
        self.coxa5_servo  = Servo(ada_servo.Servo(self.pca2.channels[3]))
        self.femur5_servo = Servo(ada_servo.Servo(self.pca2.channels[4]))
        self.tibia5_servo = Servo(ada_servo.Servo(self.pca2.channels[5]))
        self.coxa6_servo  = Servo(ada_servo.Servo(self.pca2.channels[6]))
        self.femur6_servo = Servo(ada_servo.Servo(self.pca2.channels[7]))
        self.tibia6_servo = Servo(ada_servo.Servo(self.pca2.channels[8]))

        self.all_servos: List[Servo] = [
            self.coxa1_servo, 
            self.femur1_servo,
            self.tibia1_servo,
            self.coxa2_servo,
            self.femur2_servo,
            self.tibia2_servo,
            self.coxa3_servo,
            self.femur3_servo,
            self.tibia3_servo,
            self.coxa4_servo,
            self.femur4_servo,
            self.tibia4_servo,
            self.coxa5_servo,
            self.femur5_servo,
            self.tibia5_servo,
            self.coxa6_servo,
            self.femur6_servo,
            self.tibia6_servo
            ]

if __name__ == "__main__":
    i2c = busio.I2C(SCL, SDA)
    pca1 = PCA9685(i2c, address=0x40)
    pca1.frequency = 50
    pca2 = PCA9685(i2c, address=0x41)
    pca2.frequency = 50

    #c = XboxOneController()

    a = aaa()
    s = 20
    i = s 
    while True:
        time.sleep(0.01)
        i += 1
        for s in a.all_servos:
            s.write(i)

        print(i)
        if i>179:
            i = s