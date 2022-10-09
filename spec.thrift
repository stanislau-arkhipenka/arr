

enum ButtonID {
    A,
    B,
    X,
    Y,
    SELECT,
    START,
    THUMBL,
    THUMBR,
    TL,
    TR,
    L2,
    R2,
    PAD_UP,
    PAD_DOWN,
    PAD_LEFT,
    PAD_RIGHT,
    DUMMY = 999,
}

enum AxisID {
    LX,
    LY,
    RX,
    RY,
    THROTTLE_L,
    THROTTLE_R,
}

const map<ButtonID,string> BUTTON_NAMES = {
    ButtonID.A: 'a',
    ButtonID.B: 'b',
    ButtonID.X: 'x',
    ButtonID.Y: 'y',
    ButtonID.SELECT: 'select',
    ButtonID.START: 'start',
    ButtonID.THUMBL: 'thumbl',
    ButtonID.THUMBR: 'thumbr',
    ButtonID.TL: 'tl',
    ButtonID.TR: 'tr',
    ButtonID.L2: 'l2',
    ButtonID.R2: 'r2',
    ButtonID.PAD_UP: 'pad_up',
    ButtonID.PAD_DOWN: 'pad_down',
    ButtonID.PAD_LEFT: 'pad_left',
    ButtonID.PAD_RIGHT: 'pad_right',
    
}

struct ARR_status {
    1: required i16     mode;
    2: required i16     sub_mode;
    3: required i16     speed;
    4: optional bool    light_1 = false;
    5: optional bool    light_2 = false;
    6: optional i16     battery = 0; 
}

service ARR_proto {

    bool ping(),

    oneway void axis(1:AxisID id, 2:double value),

    oneway void button(1:ButtonID id, 2:bool value),

    ARR_status get_status(),

    list<string> get_logs(1: i32 offset),

}