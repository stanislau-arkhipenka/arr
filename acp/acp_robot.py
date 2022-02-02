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
from acp.led import Led
from common import set_disposition, rconf, map
from typing import List


logger = logging.getLogger(__name__)

class AcpRobot(Hexapod):

    HEAD_TILT_CAL = [70, 125] # min, max
    HEAD_ROTATE_CAL = [107, 0] # min, max

    PCA_FREQ = 50 # Servo control freq

    def __init__(self, config_file_path: str, debug_servo: bool = False, debug_controller: bool = False):
        super().__init__(config_file_path)
        set_disposition()
        if not debug_controller:
            self.controller = XboxOneController()
        if not debug_servo:
            self._init_servo()
        self.led1 = Led(17)
        self.all_servos = []
        

    def _init_servo(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca1 = PCA9685(self.i2c, address=0x41)
        self.pca2 = PCA9685(self.i2c, address=0x40)
        self.pca1.frequency = self.PCA_FREQ
        self.pca2.frequency = self.PCA_FREQ



        self.coxa1_servo  = Servo(ada_servo.Servo(self.pca1.channels[6]))    
        self.femur1_servo = Servo(ada_servo.Servo(self.pca1.channels[7]), reverse=True)
        self.tibia1_servo = Servo(ada_servo.Servo(self.pca1.channels[8]), reverse=True)
        self.coxa2_servo  = Servo(ada_servo.Servo(self.pca1.channels[3]))
        self.femur2_servo = Servo(ada_servo.Servo(self.pca1.channels[4]), reverse=True)
        self.tibia2_servo = Servo(ada_servo.Servo(self.pca1.channels[5]), reverse=True)
        self.coxa3_servo  = Servo(ada_servo.Servo(self.pca1.channels[0]))
        self.femur3_servo = Servo(ada_servo.Servo(self.pca1.channels[1]), reverse=True)
        self.tibia3_servo = Servo(ada_servo.Servo(self.pca1.channels[2]), reverse=True)
        self.coxa4_servo  = Servo(ada_servo.Servo(self.pca2.channels[6]))
        self.femur4_servo = Servo(ada_servo.Servo(self.pca2.channels[7]))
        self.tibia4_servo = Servo(ada_servo.Servo(self.pca2.channels[8]))
        self.coxa5_servo  = Servo(ada_servo.Servo(self.pca2.channels[3]))
        self.femur5_servo = Servo(ada_servo.Servo(self.pca2.channels[4]))
        self.tibia5_servo = Servo(ada_servo.Servo(self.pca2.channels[5]))
        self.coxa6_servo  = Servo(ada_servo.Servo(self.pca2.channels[0]))
        self.femur6_servo = Servo(ada_servo.Servo(self.pca2.channels[1]))
        self.tibia6_servo = Servo(ada_servo.Servo(self.pca2.channels[2]))

        self.head_tilt = Servo(ada_servo.Servo(self.pca2.channels[13]), reverse=True)
        self.head_rotate = Servo(ada_servo.Servo(self.pca2.channels[12]))
        

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
            self.tibia6_servo,
            self.head_tilt,
            self.head_rotate
            ]

    
    def loop(self):
        if rconf.sigint:
            logger.info("CTRL+C. Terminating")
            for servo in self.all_servos:
                servo.angle = None
            self.pca1.deinit()
            self.pca2.deinit()
            self.controller.terminate()
            sys.exit(0)

        super().loop()

        if self.mode == self.MODE_WALK:
            self.control_head()


    def process_gamepad(self):
        super().process_gamepad()
        if self.controller.button_pressed(self.BUT_THUMBR):
            self.led1.change()
            logger.info("Changing lights")
    
    def control_head(self):
        commanded_head_tilt = int(map(self.controller.analog(self.AS_LY), 0, 255, self.HEAD_TILT_CAL[0], self.HEAD_TILT_CAL[1]))
        commanded_head_rotate = int(map(self.controller.analog(self.AS_LX), 0, 255, self.HEAD_ROTATE_CAL[0], self.HEAD_ROTATE_CAL[1]))
        self.head_tilt.write(commanded_head_tilt)
        self.head_rotate.write(commanded_head_rotate)

    def default_head(self):
        commanded_head_tilt = int(abs(self.HEAD_TILT_CAL[1] - self.HEAD_TILT_CAL[0]))
        commanded_head_rotate = int(abs(self.HEAD_ROTATE_CAL[1] - self.HEAD_ROTATE_CAL[0]))
        self.head_tilt.write(commanded_head_tilt)
        self.head_rotate.write(commanded_head_rotate)