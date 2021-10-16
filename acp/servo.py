import logging

logger = logging.getLogger(__name__)

class Servo:
    def __init__(self, channel) -> None:
        self.channel = channel

    def write(self, value: int) -> None:
        logger.debug("servo write %s", value)
        self.channel.angle = value

    def read(self) -> int:
        return self.channel.angle 
