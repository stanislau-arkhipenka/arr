import board
import busio
from adafruit_motor import servo as ada_servo
from adafruit_pca9685 import PCA9685
from acp.hexapod import Hexapod
from acp.servo import Servo
from acp.controller import XboxOneController

class AcpRobot(Hexapod):

    PCA_FREQ = 50 # Servo control freq

    def __init__(self, debug_servo: bool = False, debug_controller: bool = False):
        super().__init__()
        if not debug_controller:
            self.controller = XboxOneController()
        if not debug_servo:
            self._init_servo()
        
        
        

    def _init_servo(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca1 = PCA9685(self.i2c, address=0x40)
        #self.pca2 = PCA9685(self.i2c, address=0x41)
        self.pca1.frequency = self.PCA_FREQ
        #self.pca2.frequency = self.PCA_FREQ



        self.coxa1_servo  = Servo(ada_servo.Servo(self.pca1.channels[0]))     #18 servos = Servo()
        self.femur1_servo = Servo(ada_servo.Servo(self.pca1.channels[1]))
        self.tibia1_servo = Servo(ada_servo.Servo(self.pca1.channels[2]))
        self.coxa2_servo  = Servo(ada_servo.Servo(self.pca1.channels[3]))
        self.femur2_servo = Servo(ada_servo.Servo(self.pca1.channels[4]))
        self.tibia2_servo = Servo(ada_servo.Servo(self.pca1.channels[5]))
        self.coxa3_servo  = Servo(ada_servo.Servo(self.pca1.channels[6]))
        self.femur3_servo = Servo(ada_servo.Servo(self.pca1.channels[7]))
        self.tibia3_servo = Servo(ada_servo.Servo(self.pca1.channels[8]))
        self.coxa4_servo  = Servo(ada_servo.Servo(self.pca1.channels[9]))
        self.femur4_servo = Servo(ada_servo.Servo(self.pca1.channels[10]))
        self.tibia4_servo = Servo(ada_servo.Servo(self.pca1.channels[11]))
        self.coxa5_servo  = Servo(ada_servo.Servo(self.pca1.channels[12]))
        self.femur5_servo = Servo(ada_servo.Servo(self.pca1.channels[13]))
        self.tibia5_servo = Servo(ada_servo.Servo(self.pca1.channels[14]))
        self.coxa6_servo  = Servo(ada_servo.Servo(self.pca1.channels[15]))
        #self.femur6_servo = Servo(ada_servo.Servo(self.pca2.channels[0]))
        #self.tibia6_servo = Servo(ada_servo.Servo(self.pca2.channels[1]))

