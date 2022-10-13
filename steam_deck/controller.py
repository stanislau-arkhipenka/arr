import logging
import time
from spec.ttypes import ButtonID, AxisID

logger = logging.getLogger(__name__)


class SteamDeckController:

    dev_loc = "/dev/input/"

    axis_map = [
        AxisID.LX,
        AxisID.LY,
        AxisID.THROTTLE_L,
        AxisID.RX,
        AxisID.RY,
        AxisID.THROTTLE_R,
        AxisID.PAD_X,
        AxisID.PAD_Y
    ]

    button_map = [
        ButtonID.A,
        ButtonID.B,
        ButtonID.X,
        ButtonID.Y,
        ButtonID.L2,
        ButtonID.R2,
        ButtonID.SELECT, # TODO change to View button
        ButtonID.START,  # TODO change to Menu button
        ButtonID.DUMMY,  # Real button should be here! But which? 
        ButtonID.THUMBL,
        ButtonID.THUMBR,
    ]

    def __init__(self, thrift_client) -> None:
        self.fn: str = self.await_controller()

        logger.info("Connecting to controller")
        self.jsdev = open(self.fn, 'rb')

        buf = array.array('B', [0] * 64)
        ioctl(self.jsdev, 0x80006a13 + (0x10000 * len(buf)), buf)
        self.js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
        logger.info('Device name: %s', self.js_name)

        self.monitor_thread = threading.Thread(target=self._monitor_dev)
        self.monitor_dev()

    def await_controller(self) -> str:
        logger.info("Waiting for controller")
        while True:
            for fn in os.listdir(self.dev_loc):
                if fn.startswith('js'):
                    logger.info( 'Controller found: %s%s', self.dev_loc, fn)
                    return f"{self.dev_loc}{fn}"
                else:
                    logger.warning("Controller not found")
                    time.sleep(1)


    def monitor_dev(self) -> None:
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
                    logger.debug("= %s %s -> %s", value, number, self.button_map[number])


                elif type & 0x02:
                    if str(number) == sys.argv[1]:
                        logger.debug("= %s %s -> %s", value, number, self.axis_map[number])

                    if number == 6 and value == -32767:
                        pass # TODO ButtonID.PAD_LEFT
                    elif number == 6 and value == 32767:
                        pass # TODO ButtonID.PAD_RIGHT 
                    elif number == 7 and value == -32767:
                        pass # TODO ButtonID.PAD_UP
                    elif number == 8 and value == 32767:
                        pass # TODO ButtonID.PAD_DOWN

    def terminate(self) -> None:
        self._terminate_monitor = True
        self.monitor_thread.join()
        return