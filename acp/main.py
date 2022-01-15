import click
import logging
from acp.acp_robot import AcpRobot
from acp.controller import XboxOneController
from acp.hexapod import DummyServo

@click.command()
@click.argument("config_file_path", default="./robot_config.json")
@click.option("--debug-servo", is_flag=True, default=False)
@click.option("--debug-controller", is_flag=True, default=False)
def main(config_file_path, debug_servo, debug_controller):
    AcpRobot(config_file_path, debug_servo=debug_servo, debug_controller=debug_controller).run()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )
    main()
