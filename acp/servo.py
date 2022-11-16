import logging

logger = logging.getLogger(__name__)

class Servo:
    def __init__(self, channel, reverse: bool = False) -> None:
        self.channel = channel
        self.reverse = reverse

    def write(self, value: int) -> None:
        # logger.debug("servo write %s", value)
        try:
            self.channel.angle = self._rev(value)
        except OSError:
            logger.error("Unable to write servo[%s] = %s", self.channel, value)

    def read(self) -> int:
        return self._rev(self.channel.angle)

    def disable(self) -> None:
        self.channel.duty_cycle = 0

    def _rev(self, value: int) -> int:
        if self.reverse:
            return self.channel.actuation_range - value
        else:
            return value
