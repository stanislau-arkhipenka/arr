import sys
import pprint
if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse
from thrift.transport import TTransport, TSocket, TSSLSocket, THttpClient
from thrift.protocol.TBinaryProtocol import TBinaryProtocol

from spec import ARR_proto
from spec.ttypes import *

def connect():
    socket = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol(transport)
    client = ARR_proto.Client(protocol)
    transport.open()

    return client