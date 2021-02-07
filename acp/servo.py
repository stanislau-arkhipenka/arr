import logging

class Servo:
    def __init__(self, channel) -> None:
        self.channel = channel

    def write(self, value: int) -> None:
        logging.debug(f"servo write {value}")
        if value > 0xffff:
            raise ValueError("Write value shoulbe be less %s" % 0xffff)
        self.channel.duty_cycle = value

    def read(self) -> int:
        self.channel.duty_cycle 
