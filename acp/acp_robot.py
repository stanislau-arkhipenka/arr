import time
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
from acp.hexapod import Hexapod
from acp.servo import Servo
from acp.controller import XboxOneController

class AcpRobot(Hexapod):

    PCA_FREQ = 50 # Servo control freq

    def __init__(self):
        super().__init__()
        self.controller = XboxOneController()
        self.i2c = busio.I2C(board.SCL, board.SDA)
        # self.pca1 = adafruit_pca9685.PCA9685(i2c, address=0x40)
        # self.pca2 = adafruit_pca9685.PCA9685(i2c, address=0x40) # TODO change address
        # self.pca1.frequency = PCA_FREQ
        # self.pca1.frequency = PCA_FREQ

        self.servo_kit_1 = ServoKit(channels=16, i2c=self.i2c,address=0x40)
        self.servo_kit_2 = ServoKit(channels=16, i2c=self.i2c,address=0x40) # TODO change address

        self.coxa1_servo  = Servo(self.servo_kit_1.servo[0])     #18 servos = Servo()
        self.femur1_servo = Servo(self.servo_kit_1.servo[1])
        self.tibia1_servo = Servo(self.servo_kit_1.servo[2])
        self.coxa2_servo  = Servo(self.servo_kit_1.servo[3])
        self.femur2_servo = Servo(self.servo_kit_1.servo[4])
        self.tibia2_servo = Servo(self.servo_kit_1.servo[5])
        self.coxa3_servo  = Servo(self.servo_kit_1.servo[6])
        self.femur3_servo = Servo(self.servo_kit_1.servo[7])
        self.tibia3_servo = Servo(self.servo_kit_1.servo[8])
        self.coxa4_servo  = Servo(self.servo_kit_1.servo[9])
        self.femur4_servo = Servo(self.servo_kit_1.servo[10])
        self.tibia4_servo = Servo(self.servo_kit_1.servo[11])
        self.coxa5_servo  = Servo(self.servo_kit_1.servo[12])
        self.femur5_servo = Servo(self.servo_kit_1.servo[13])
        self.tibia5_servo = Servo(self.servo_kit_1.servo[14])
        self.coxa6_servo  = Servo(self.servo_kit_1.servo[15])
        self.femur6_servo = Servo(self.servo_kit_2.servo[0])
        self.tibia6_servo = Servo(self.servo_kit_2.servo[1])

    def run(self) -> None:
        while(True):
            self.loop()
            time.sleep(0.01)