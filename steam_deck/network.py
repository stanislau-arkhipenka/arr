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
from threading import Lock

lock = Lock()

def ensure_lock(f):
    def wrapper(*args, **kwargs):
        lock.acquire()
        out = f(*args, **kwargs)
        lock.release()
        return out
    return wrapper

class LockedClient(Client):

    @ensure_lock
    def ping(self, *args, **kwargs):
        return super().ping(*args, **kwargs)

    @ensure_lock
    def axis(self, *args, **kwargs):
        return super().axis(*args, **kwargs)

    @ensure_lock
    def get_logs(self, *args, **kwargs):
        return super().get_logs(*args, **kwargs)

    @ensure_lock
    def get_status(self, *args, **kwargs):
        return super().get_status(*args, **kwargs)

def connect(host: str, port: int):
    socket = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol(transport)
    client = LockedClient(protocol)
    transport.open()

    return socket, client