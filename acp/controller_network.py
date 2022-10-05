import logging
import time
import spec.ARR_proto as ARR_proto

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from spec.ttypes import AxisID, ButtonID

from controller_base import ControllerBase

logger = logging.getLogger(__name__)


class _NetworkController:

    def __init__(self, button_status, axises_status):
        self._button_status = button_status
        self._axises_status = axises_status

    def ping(self) -> bool:
        return True

    def axis(self, id, value):
        axis_name = AxisID._VALUES_TO_NAMES[id].lower() # TODO remove lower() after migration to thrift
        self._axises_status[axis_name] = int(value) # TODO remove lower() after migration to thrift

    def button(self, id, value):
        button_name = ButtonID._VALUES_TO_NAMES[id].lower()
        self._button_status[button_name] = int(value)

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



