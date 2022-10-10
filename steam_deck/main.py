import logging
from ui import SteamDeckUI


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )

    s_ui = SteamDeckUI()
    s_ui.run()