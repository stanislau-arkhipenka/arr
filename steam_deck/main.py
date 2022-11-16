import logging
from ui import SteamDeckUI


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )

    s_ui = SteamDeckUI()
    s_ui.run()