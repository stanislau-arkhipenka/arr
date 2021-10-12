import logging

logger = logging.getLogger(__name__)

class Servo:
    def __init__(self, channel) -> None:
        self.channel = channel

    def write(self, value: int) -> None:
        logger.debug(f"servo write {value}")
        if value > 0xffff:
            raise ValueError("Write value shoulbe be less %s" % 0xffff)
        self.channel.duty_cycle = value

    def read(self) -> int:
        return self.channel.duty_cycle 
