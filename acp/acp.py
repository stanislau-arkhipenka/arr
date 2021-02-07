import time
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
from .hexapod import Hexapod
from .servo import Servo
from .controller import Controller

class Acp(Hexapod):

    PCA_FREQ = 50 # Servo control freq

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        # self.pca1 = adafruit_pca9685.PCA9685(i2c, address=0x40)
        # self.pca2 = adafruit_pca9685.PCA9685(i2c, address=0x40) # TODO change address
        # self.pca1.frequency = PCA_FREQ
        # self.pca1.frequency = PCA_FREQ

        self.servo_kit_1 = ServoKit(channels=16, i2c=self.i2c,adress=0x40)
        self.servo_kit_2 = ServoKit(channels=16, i2c=self.i2c,adress=0x40) # TODO change address

        self.coxa1_servo  = Servo(self.servo_ki1_1[0])     #18 servos = Servo()
        self.femur1_servo = Servo(self.servo_ki1_1[1])
        self.tibia1_servo = Servo(self.servo_ki1_1[2])
        self.coxa2_servo  = Servo(self.servo_ki1_1[3])
        self.femur2_servo = Servo(self.servo_ki1_1[4])
        self.tibia2_servo = Servo(self.servo_ki1_1[5])
        self.coxa3_servo  = Servo(self.servo_ki1_1[6])
        self.femur3_servo = Servo(self.servo_ki1_1[7])
        self.tibia3_servo = Servo(self.servo_ki1_1[8])
        self.coxa4_servo  = Servo(self.servo_ki1_1[9])
        self.femur4_servo = Servo(self.servo_ki1_1[10])
        self.tibia4_servo = Servo(self.servo_ki1_1[11])
        self.coxa5_servo  = Servo(self.servo_ki1_1[12])
        self.femur5_servo = Servo(self.servo_ki1_1[13])
        self.tibia5_servo = Servo(self.servo_ki1_1[14])
        self.coxa6_servo  = Servo(self.servo_ki1_1[15])
        self.femur6_servo = Servo(self.servo_ki1_2[0])
        self.tibia6_servo = Servo(self.servo_ki1_2[1])

    def run(self) -> None:
        while(True):
            self.loop()
            time.sleep(0.01)