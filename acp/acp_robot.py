import os
import logging
import sys
import signal
from acp.hexapod import Hexapod
from acp.servo import Servo
from acp.controller_xbox import XboxOneController
from acp.controller_network import NetworkController
from common import set_disposition, rconf, map
from typing import List
from dummy import DummyServo, DummyLed


logger = logging.getLogger(__name__)

class AcpRobot(Hexapod):

    HEAD_TILT_CAL = [50, 120] # min, max
    HEAD_ROTATE_CAL = [107, 0] # min, max

    PCA_FREQ = 50 # Servo control freq

    CONTROLLERS = {
        "xbox": XboxOneController,
        "network": NetworkController
    }

    def __init__(self, config_file_path: str,
            controller: str = "xbox", 
            debug_servo: bool = False, 
            debug_led: bool = False):
        super().__init__(config_file_path)
        set_disposition()
        
        if controller in self.CONTROLLERS:
            self.controller = self.CONTROLLERS.get(controller)()
        elif controller is None:
            logger.warning("No controller provided")
        else:
            raise ValueError("Controller %s not found. Valid options: %s", self.CONTROLLERS)
        self.debug_servo = debug_servo
        if not debug_servo:
            import busio
            from adafruit_motor import servo as ada_servo
            from adafruit_pca9685 import PCA9685
            try:
                import board
            except NotImplementedError:
                board = object()     
            self._init_servo()
        else:
            self.head_tilt = DummyServo()
            self.head_rotate = DummyServo()
        if not debug_led:
            from acp.led import Led
            self.led1 = Led(17)
            self.led2 = Led(18)
        else:
            self.led1 = DummyLed(1)
            self.led2 = DummyLed(2)
        self.all_servos = []
        

    def _init_servo(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.pca1 = PCA9685(self.i2c, address=0x41)
        self.pca2 = PCA9685(self.i2c, address=0x40)
        self.pca1.frequency = self.PCA_FREQ
        self.pca2.frequency = self.PCA_FREQ

        self.coxa1_servo  = Servo(ada_servo.Servo(self.pca2.channels[6]))
        self.femur1_servo = Servo(ada_servo.Servo(self.pca2.channels[7]))
        self.tibia1_servo = Servo(ada_servo.Servo(self.pca2.channels[8]))
        self.coxa2_servo  = Servo(ada_servo.Servo(self.pca2.channels[3]))
        self.femur2_servo = Servo(ada_servo.Servo(self.pca2.channels[4]))
        self.tibia2_servo = Servo(ada_servo.Servo(self.pca2.channels[5]))
        self.coxa3_servo  = Servo(ada_servo.Servo(self.pca2.channels[0]))
        self.femur3_servo = Servo(ada_servo.Servo(self.pca2.channels[1]))
        self.tibia3_servo = Servo(ada_servo.Servo(self.pca2.channels[2]))
        self.coxa4_servo  = Servo(ada_servo.Servo(self.pca1.channels[6]))
        self.femur4_servo = Servo(ada_servo.Servo(self.pca1.channels[7]), reverse=True)
        self.tibia4_servo = Servo(ada_servo.Servo(self.pca1.channels[8]), reverse=True)
        self.coxa5_servo  = Servo(ada_servo.Servo(self.pca1.channels[3]))
        self.femur5_servo = Servo(ada_servo.Servo(self.pca1.channels[4]), reverse=True)
        self.tibia5_servo = Servo(ada_servo.Servo(self.pca1.channels[5]), reverse=True)
        self.coxa6_servo  = Servo(ada_servo.Servo(self.pca1.channels[0]))
        self.femur6_servo = Servo(ada_servo.Servo(self.pca1.channels[1]), reverse=True)
        self.tibia6_servo = Servo(ada_servo.Servo(self.pca1.channels[2]), reverse=True)


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
            self.led1.off()
            self.led2.off()
            if not self.debug_servo:
                for servo in self.all_servos:
                    servo.angle = None
                self.pca1.deinit()
                self.pca2.deinit()
            # Yeah... I know, but thrift thread doesn't have stop method
            os.kill(os.getpid(), 9)

        super().loop()

        if self.mode == self.MODE_WALK:
            self.control_head()
        else:
            self.default_head()


    def process_gamepad(self):
        super().process_gamepad()
        if self.controller.button_pressed(self.BUT_THUMBR):
            self.led1.change()
            logger.info("Changing lights")
        if self.controller.button_pressed(self.BUT_THUMBL):
            self.led2.change()
            logger.info("Changing main light")

    
    def control_head(self):
        commanded_head_tilt = int(map(self.controller.analog(self.AS_LY), 0, 255, self.HEAD_TILT_CAL[0], self.HEAD_TILT_CAL[1]))
        commanded_head_rotate = int(map(self.controller.analog(self.AS_LX), 0, 255, self.HEAD_ROTATE_CAL[0], self.HEAD_ROTATE_CAL[1]))
        self.head_tilt.write(commanded_head_tilt)
        self.head_rotate.write(commanded_head_rotate)

    def default_head(self):
        commanded_head_tilt = int(map(127, 0, 255, self.HEAD_TILT_CAL[0], self.HEAD_TILT_CAL[1]))
        commanded_head_rotate = int(map(127, 0, 255, self.HEAD_ROTATE_CAL[0], self.HEAD_ROTATE_CAL[1]))
        self.head_tilt.write(commanded_head_tilt)
        self.head_rotate.write(commanded_head_rotate)