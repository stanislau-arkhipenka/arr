import asyncio
import sys
import logging
import time
from typing import Union, Dict, List
import os, struct, array
from fcntl import ioctl
import threading
from common import map

logger = logging.getLogger(__name__)

class XboxOneController:

    dev_loc = "/dev/input/"

    FRAME_TIME_MS = 20

    axis_names = {
        0x00 : 'lx',
        0x01 : 'ly',
        0x02 : 'throttle_l',
        0x03 : 'rx',
        0x04 : 'ry',
        0x05 : 'throttle_r',
        0x06 : 'other_1',
        0x07 : 'other_2',
        0x08 : 'other_3',
        0x09 : 'other_4',
        0x0a : 'other_5',
        0x10 : 'hat0x',
        0x11 : 'hat0y',
        0x12 : 'hat1x',
        0x13 : 'hat1y',
        0x14 : 'hat2x',
        0x15 : 'hat2y',
        0x16 : 'hat3x',
        0x17 : 'hat3y',
        0x18 : 'other_6',
        0x19 : 'other_7',
        0x1a : 'other_8',
        0x1b : 'other_9',
        0x1c : 'other_10',
        0x20 : 'other_11',
        0x28 : 'misc',
    }

    button_names = {
        0x120 : 'trigger',
        0x121 : 'thumb',
        0x122 : 'thumb2',
        0x123 : 'top',
        0x124 : 'top2',
        0x125 : 'pinkie',
        0x126 : 'base',
        0x127 : 'base2',
        0x128 : 'base3',
        0x129 : 'base4',
        0x12a : 'base5',
        0x12b : 'base6',
        0x12f : 'dead',
        0x130 : 'a',
        0x131 : 'b',
        0x132 : 'c',
        0x133 : 'x',
        0x134 : 'y',
        0x135 : 'z',
        0x136 : 'tl',
        0x137 : 'tr',
        0x138 : 'tl2',
        0x139 : 'tr2',
        0x13a : 'select',
        0x13b : 'start',
        0x13c : 'mode',
        0x13d : 'thumbl',
        0x13e : 'thumbr',

        0x220 : 'dpad_up',
        0x221 : 'dpad_down',
        0x222 : 'dpad_left',
        0x223 : 'dpad_right',

        # XBox 360 controller uses these codes.
        0x2c0 : 'dpad_left',
        0x2c1 : 'dpad_right',
        0x2c2 : 'dpad_up',
        0x2c3 : 'dpad_down',
    }

    def __init__(self, **kwargs):
        self.axis_states: Dict[str,int] = {}
        self.axis_states_ts: Dict = {}
        self.button_states: Dict = {}
        self.slow_button_old: Dict = {}
        self.slow_button_new: Dict = {}
        self.axis_map: List = []
        self.button_map: List = []
        self.fn: str = self.await_controller()

        logger.info("Connecting to controller")
        self.jsdev = open(self.fn, 'rb')

        # Get the device name.
        #buf = bytearray(63)
        buf = array.array('B', [0] * 64)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        self.js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
        logger.info('Device name: %s', self.js_name)

        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a11, buf) # JSIOCGAXES
        self.num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
        self.num_buttons = buf[0]

        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.jsdev, 0x80406a32, buf) # JSIOCGAXMAP

        for axis in buf[:self.num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axis_map.append(axis_name)
            self.axis_states[axis_name] = 0.0
    
        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

        for btn in buf[:self.num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.button_map.append(btn_name)
            self.button_states[btn_name] = 0

        logger.info('%d axes found: %s' % (self.num_axes, ', '.join(self.axis_map)))
        logger.info('%d buttons found: %s' % (self.num_buttons, ', '.join(self.button_map)))

        self.monitor_thread = threading.Thread(target=self._monitor_dev)
        self.monitor_dev()

    def await_controller(self):
        logger.info("Waiting for controller")
        while True:
            for fn in os.listdir(self.dev_loc):
                if fn.startswith('js'):
                    logger.info( 'Controller found: %s%s', self.dev_loc, fn)
                    return f"{self.dev_loc}{fn}"
                else:
                    logger.warning("Controller not found")
                    time.sleep(1)


    def monitor_dev(self):
        self._terminate_monitor: bool = False
        self.monitor_thread.start()
        

    def _monitor_dev(self, vibrate: bool = False) -> None:   # TODO vibrate not implemented
        while True:
            if self._terminate_monitor:
                return
            self.evbuf = self.jsdev.read(8)
            if self.evbuf:
                time1, value, type, number = struct.unpack('IhBB', self.evbuf)
                if type & 0x01:
                    button = self.button_map[number]
                    if button:
                        self.button_states[button] = value
                        if value:
                            logger.debug("%s pressed, %s", button, time1)
                        else:
                            logger.debug("%s released, %s", button, time1)

                elif type & 0x02:
                    axis = self.axis_map[number]
                    if axis:
                        fvalue = value / 32767.0
                        if axis in ['hat0x', 'hat0y']:  # hack for dpad
                            self.button_states[axis] = int(fvalue)
                            tmp_int =  int(fvalue)
                            self.button_states["pad_up"] = 1 if axis == 'hat0y' and tmp_int == -1 else 0
                            self.button_states["pad_down"] = 1 if axis == 'hat0y' and tmp_int == 1 else 0
                            self.button_states['pad_left'] = 1 if axis == 'hat0x' and tmp_int == -1 else 0
                            self.button_states['pad_right'] = 1 if axis == 'hat0x' and tmp_int == 1 else 0
                        
                        self.axis_states[axis] = int(map(fvalue, -1.0, 1.0, 0, 255))    # AFAIK hexapod expects int between 0 and 255
                        logger.debug("%s: %.3f -> %s" % (axis, fvalue, self.axis_states[axis]))

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
    c = XboxOneController()
    while True:
        time.sleep(0.1)
        logger.info(c.axis_states)
