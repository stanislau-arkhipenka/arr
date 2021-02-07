from pyPS4Controller.controller import Controller as Ps4Controller

class Controller(Ps4Controller):

    PSB_PAD_DOWN =  1
    PSB_PAD_LEFT =  2
    PSB_PAD_UP =    3
    PSB_PAD_RIGHT = 4
    PSB_TRIANGLE =  5
    PSB_SQUARE =    6
    PSB_CIRCLE =    7
    PSB_CROSS =     8
    PSB_START =     9
    PSB_L1  =       10
    PSB_R1  =       11
    PSS_RX =        12
    PSS_RY =        13
    PSS_LX =        14
    PSS_LY =        15

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

