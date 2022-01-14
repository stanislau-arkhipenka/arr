import logging
import signal
from typing import List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RuntimeConfig:
    sigint: bool = False

rconf = RuntimeConfig()

def signal_handler(sig: int, frame) -> None:
    rconf.sigint = True

def set_disposition() -> None:
    logger.info("Setting disposition")
    signal.signal(signal.SIGINT, signal_handler)

def map(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def constrain(x: float, a: float, b: float) -> float:
    assert a <= b
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x
