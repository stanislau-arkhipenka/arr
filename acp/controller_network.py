import queue
import logging
import time
import spec.ARR_proto as ARR_proto
from logging.handlers import QueueHandler
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from threading import Lock
from spec.ttypes import AxisID, ButtonID, ARR_status

from controller_base import ControllerBase

logger = logging.getLogger(__name__)
lock = Lock()

def _ensure_single(f):
    def wrapper(*args, **kwargs):
        lock.acquire()
        out = f(*args, **kwargs)
        lock.release()
        return out
    return wrapper

class _NetworkController:

    def __init__(self, button_status, axises_status):
        self._button_status = button_status
        self._axises_status = axises_status
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.queue_handler)

    @_ensure_single
    def ping(self) -> bool:
        logger.info("ping")
        return True

    @_ensure_single
    def axis(self, id, value):
        axis_name = AxisID._VALUES_TO_NAMES[id].lower() # TODO remove lower() after migration to thrift
        self._axises_status[axis_name] = int(value) # TODO remove lower() after migration to thrift

    @_ensure_single
    def button(self, id, value):
        button_name = ButtonID._VALUES_TO_NAMES[id].lower()
        self._button_status[button_name] = int(value)
    
    @_ensure_single
    def get_logs(self, offset: int):
        out: List[str] = []
        
        while not self.log_queue.empty():
            msg = self.log_queue.get(False).getMessage()
            out.append(msg)
        return out
    
    @_ensure_single
    def get_status(self):
        return ARR_status(
            mode = 0,
            sub_mode = 0,
            speed = 0,
            light_1 = False,
            light_2 = False,
            battery = 100;
        )


class NetworkController(ControllerBase):
    def __init__(self) -> None:
        super().__init__()
        

    def _monitor_dev(self, vibrate: bool = False) -> None:
        handler = _NetworkController(self.button_states, self.axis_states)
        processor = ARR_proto.Processor(handler)
        transport = TSocket.TServerSocket(port=9090)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        logger.info('Starting network the server...')
        server.serve()


if __name__ == '__main__':


    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s][%(name)s] %(message)s",
        handlers=[
        logging.StreamHandler()
        ]
    )

    c = NetworkController()
    while True:
        print(c.button_states)
        time.sleep(0.1)



