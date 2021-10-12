import logging
from acp.acp_robot import AcpRobot
from acp.controller import XboxOneController
from acp.hexapod import DummyServo



if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )
    AcpRobot(debug_servo=True, debug_controller=False).run()
