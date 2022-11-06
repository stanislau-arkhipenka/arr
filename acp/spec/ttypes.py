#
# Autogenerated by Thrift Compiler (0.13.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TFrozenDict, TException, TApplicationException
from thrift.protocol.TProtocol import TProtocolException
from thrift.TRecursive import fix_spec

import sys

from thrift.transport import TTransport
all_structs = []


class ButtonID(object):
    A = 0
    B = 1
    X = 2
    Y = 3
    SELECT = 4
    START = 5
    THUMBL = 6
    THUMBR = 7
    TL = 8
    TR = 9
    L2 = 10
    R2 = 11
    PAD_UP = 12
    PAD_DOWN = 13
    PAD_LEFT = 14
    PAD_RIGHT = 15
    DUMMY = 999

    _VALUES_TO_NAMES = {
        0: "A",
        1: "B",
        2: "X",
        3: "Y",
        4: "SELECT",
        5: "START",
        6: "THUMBL",
        7: "THUMBR",
        8: "TL",
        9: "TR",
        10: "L2",
        11: "R2",
        12: "PAD_UP",
        13: "PAD_DOWN",
        14: "PAD_LEFT",
        15: "PAD_RIGHT",
        999: "DUMMY",
    }

    _NAMES_TO_VALUES = {
        "A": 0,
        "B": 1,
        "X": 2,
        "Y": 3,
        "SELECT": 4,
        "START": 5,
        "THUMBL": 6,
        "THUMBR": 7,
        "TL": 8,
        "TR": 9,
        "L2": 10,
        "R2": 11,
        "PAD_UP": 12,
        "PAD_DOWN": 13,
        "PAD_LEFT": 14,
        "PAD_RIGHT": 15,
        "DUMMY": 999,
    }


class AxisID(object):
    LX = 0
    LY = 1
    RX = 2
    RY = 3
    THROTTLE_L = 4
    THROTTLE_R = 5
    PAD_X = 6
    PAD_Y = 7

    _VALUES_TO_NAMES = {
        0: "LX",
        1: "LY",
        2: "RX",
        3: "RY",
        4: "THROTTLE_L",
        5: "THROTTLE_R",
        6: "PAD_X",
        7: "PAD_Y",
    }

    _NAMES_TO_VALUES = {
        "LX": 0,
        "LY": 1,
        "RX": 2,
        "RY": 3,
        "THROTTLE_L": 4,
        "THROTTLE_R": 5,
        "PAD_X": 6,
        "PAD_Y": 7,
    }


class Mode(object):
    IDLE = 0
    WALK = 1
    CXYZ = 2
    CYPR = 3
    OLEG = 4
    CALI = 99

    _VALUES_TO_NAMES = {
        0: "IDLE",
        1: "WALK",
        2: "CXYZ",
        3: "CYPR",
        4: "OLEG",
        99: "CALI",
    }

    _NAMES_TO_VALUES = {
        "IDLE": 0,
        "WALK": 1,
        "CXYZ": 2,
        "CYPR": 3,
        "OLEG": 4,
        "CALI": 99,
    }


class ARR_status(object):
    """
    Attributes:
     - mode
     - sub_mode
     - speed
     - light_1
     - light_2
     - battery

    """


    def __init__(self, mode=None, sub_mode=None, speed=None, light_1=False, light_2=False, battery=0,):
        self.mode = mode
        self.sub_mode = sub_mode
        self.speed = speed
        self.light_1 = light_1
        self.light_2 = light_2
        self.battery = battery

    def read(self, iprot):
        if iprot._fast_decode is not None and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None:
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.I16:
                    self.mode = iprot.readI16()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I16:
                    self.sub_mode = iprot.readI16()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I16:
                    self.speed = iprot.readI16()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.BOOL:
                    self.light_1 = iprot.readBool()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.BOOL:
                    self.light_2 = iprot.readBool()
                else:
                    iprot.skip(ftype)
            elif fid == 6:
                if ftype == TType.I16:
                    self.battery = iprot.readI16()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(oprot._fast_encode(self, [self.__class__, self.thrift_spec]))
            return
        oprot.writeStructBegin('ARR_status')
        if self.mode is not None:
            oprot.writeFieldBegin('mode', TType.I16, 1)
            oprot.writeI16(self.mode)
            oprot.writeFieldEnd()
        if self.sub_mode is not None:
            oprot.writeFieldBegin('sub_mode', TType.I16, 2)
            oprot.writeI16(self.sub_mode)
            oprot.writeFieldEnd()
        if self.speed is not None:
            oprot.writeFieldBegin('speed', TType.I16, 3)
            oprot.writeI16(self.speed)
            oprot.writeFieldEnd()
        if self.light_1 is not None:
            oprot.writeFieldBegin('light_1', TType.BOOL, 4)
            oprot.writeBool(self.light_1)
            oprot.writeFieldEnd()
        if self.light_2 is not None:
            oprot.writeFieldBegin('light_2', TType.BOOL, 5)
            oprot.writeBool(self.light_2)
            oprot.writeFieldEnd()
        if self.battery is not None:
            oprot.writeFieldBegin('battery', TType.I16, 6)
            oprot.writeI16(self.battery)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        if self.mode is None:
            raise TProtocolException(message='Required field mode is unset!')
        if self.sub_mode is None:
            raise TProtocolException(message='Required field sub_mode is unset!')
        if self.speed is None:
            raise TProtocolException(message='Required field speed is unset!')
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.items()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)
all_structs.append(ARR_status)
ARR_status.thrift_spec = (
    None,  # 0
    (1, TType.I16, 'mode', None, None, ),  # 1
    (2, TType.I16, 'sub_mode', None, None, ),  # 2
    (3, TType.I16, 'speed', None, None, ),  # 3
    (4, TType.BOOL, 'light_1', None, False, ),  # 4
    (5, TType.BOOL, 'light_2', None, False, ),  # 5
    (6, TType.I16, 'battery', None, 0, ),  # 6
)
fix_spec(all_structs)
del all_structs
