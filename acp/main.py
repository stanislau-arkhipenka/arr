from email.policy import default
import click
import logging
from acp.acp_robot import AcpRobot

@click.command()
@click.argument("config_file_path", default="./robot_config.json")
@click.option("--controller", type=str)
@click.option("--debug-servo", is_flag=True, default=False)
@click.option("--debug-led", is_flag=True, default=False)
@click.option("--log-level", type=str, default="INFO")
def main(config_file_path, controller=None, debug_servo=False, debug_led=False, log_level="INFO"):
    level = logging.getLevelName(log_level)
    logging.basicConfig(
        level=level,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )
    AcpRobot(config_file_path, controller=controller, debug_servo=debug_servo, debug_led=debug_led).run()


if __name__ == "__main__":

    main()
