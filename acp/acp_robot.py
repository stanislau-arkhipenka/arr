import logging
import sys
import signal
import board
import busio
from adafruit_motor import servo as ada_servo
from adafruit_pca9685 import PCA9685
from acp.hexapod import Hexapod
from acp.servo import Servo
from acp.controller import XboxOneController
from common import set_disposition, rconf
from typing import List

class AcpRobot(Hexapod):

    PCA_FREQ = 50 # Servo control freq

    def __init__(self, config_file_path: str, debug_servo: bool = False, debug_controller: bool = False):
        super().__init__(config_file_path)
        set_disposition()
        if not debug_controller:
            self.controller = XboxOneController()
        if not debug_servo:
            self._init_servo()
        

    def _init_servo(self):
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

    def _loop_hook(self):
        if rconf.sigint:
            logging.info("CTRL+C. Terminating")
            for servo in self.all_servos:
                servo.angle = None
            self.pca1.deinit()
            self.pca2.deinit()
            self.controller.terminate()
            sys.exit(0)
            

