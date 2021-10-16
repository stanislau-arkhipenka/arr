import logging
from acp.acp_robot import AcpRobot
from acp.controller import XboxOneController
from acp.hexapod import DummyServo



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )
    AcpRobot(debug_servo=False, debug_controller=False).run()
