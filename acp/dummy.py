import logging

logger = logging.getLogger(__name__)


class DummyServo:
  def __init__(self):
    self.value = 0

  def write(self, value: int):
    if self.value != value:
      logger.debug(f"servo write {value}")
      self.value = value

  def read(self):
    logger.debug(f"servo read {self.value}")
    return self.value


class DummyController:
  def __init__(self):
    pass

  def analog(self, id):
    return 1

  def button_pressed(self, button: int):
    logger.debug("button_pressed %s", button)
    return False

  def button(self, button: int) -> bool:
    logger.debug("button %s", button)
    return False

  def read_gamepad(self, vibrate: int):
    pass
  
  def terminate(self) -> None:
    pass


class DummyLed:

    def __init__(self, id: int):
        self.id = id
        self.state = False

    def change(self):
        if self.state:
            self.off()
        else:
            self.on()
        self.state = not self.state

    def on(self):
        logger.debug("LED %s set to ON", self.id)
    
    def off(self):
        logger.debug("LED %s set to OFF", self.id)