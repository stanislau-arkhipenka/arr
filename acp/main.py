from acp.acp_robot import AcpRobot
from acp.controller import XboxOneController
from acp.hexapod import DummyServo



if __name__ == "__main__":
    AcpRobot(debug_servo=False, debug_controller=False).run()
