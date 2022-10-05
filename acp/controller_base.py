import logging
import time
from typing import Union, Dict, List
from spec.ttypes import ButtonID, AxisID
import threading

logger = logging.getLogger(__name__)

class ControllerBase:

    def __init__(self, **kwargs):
        self.axis_states: Dict[str,int] = {}
        self.axis_states_ts: Dict = {}
        self.button_states: Dict = {}
        self.slow_button_old: Dict = {}
        self.slow_button_new: Dict = {}
        self.await_controller()

        for axis in AxisID._NAMES_TO_VALUES:
            self.axis_states[axis.lower()] = 0.0    # TODO remove lower() after migration to thrift

        for btn in ButtonID._NAMES_TO_VALUES:
            self.button_states[btn.lower()] = 0     # TODO remove lower() after migration to thrift

        self.monitor_thread = threading.Thread(target=self._monitor_dev)
        self.monitor_dev()

    def await_controller(self):
        pass

    def monitor_dev(self):
        self._terminate_monitor: bool = False
        self.monitor_thread.start()
        
    def _monitor_dev(self, vibrate: bool = False) -> None:
        raise NotImplemented

    def button_pressed(self, button_id: str) -> bool: # If button changed possition from unpressed to pressed
        return self.slow_button_old.get(button_id, 0) == 0 and self.slow_button_new.get(button_id, 0) == 1

    def button_released(self, button_id: str) -> bool: 
        return self.slow_button_old.get(button_id, 0) == 1 and self.slow_button_new.get(button_id, 0) == 0

    def button(self, button_id: str) -> bool: # Just read if button is pressed right now
        return self.slow_button_new.get(button_id, 0) == 1

    def analog(self, analog_id: str, to_bin: bool = False) -> Union[float,bool]:
        return analog_id > 0.5 if to_bin else self.axis_states[analog_id]

    def read_gamepad(self, vibrate: bool = False):
        self.slow_button_old: Dict = self.slow_button_new.copy()
        self.slow_button_new: Dict = self.button_states.copy()

    def terminate(self) -> None:
        self._terminate_monitor = True
        self.monitor_thread.join()
        return


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )
    c = BaseController()
    while True:
        time.sleep(0.1)
        logger.info(c.axis_states)
