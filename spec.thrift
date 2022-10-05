


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

    oneway void analog(1:i16 id, 2:double value),

    oneway void button(1:i16 id, 2:bool value),

    ARR_status get_status(),

    list<string> get_logs(1: i32 offset),

}