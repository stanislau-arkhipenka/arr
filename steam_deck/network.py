import sys
import pprint
if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
from thrift.transport import TTransport, TSocket, TSSLSocket, THttpClient
from thrift.protocol.TBinaryProtocol import TBinaryProtocol

from spec.ARR_proto import Client
from spec.ttypes import *

def connect(host: str, port: int):
    socket = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol(transport)
    client = Client(protocol)
    transport.open()

    return client