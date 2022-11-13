import logging
import time
import PySimpleGUI as sg

from controller import SteamDeckController
from video_stream import VideoStream
from network import connect, LockedClient
from typing import Any, Dict, List, Optional
from spec.ttypes import ARR_status, Mode, Giat
import queue
from thrift.transport.TTransport import TTransportException

logger = logging.getLogger(__name__)

class SteamDeckUI:

    FONT = ("Arial", 22)
    IMG_SIZE = (1280, 670) # horizontal / vertical

    def __init__(self):
        self.connected = False
        self.network_client = None
        self.network_socket = None
        self.video_stream = None
        self.logs_view = True
        self._connect_layout = None
        self._op_layout = None

        self.ui_state: Dict[str, Any] = {}

        self.init_connect_window()
        self.event_routes = {
            "_button_connect": self._button_connect,
            "_button_disconnect": self._button_disconnect,
            "_button_ping": self._button_ping,
            "_button_view": self._button_view
        }
        self.unable_connect_count = 0
        self.controller: Optional[SteamDeckController] = None

    def init_connect_window(self):
        self._connect_layout = self.get_connect_layout()
        self.window = sg.Window("Connect", self._connect_layout, finalize=True, font=self.FONT)
    
    def init_op_window(self):
        self._op_layout = self.get_op_layout()
        self.window = sg.Window("Operational Panel", self._op_layout, font=self.FONT).Finalize()
        self.window.Maximize()

    def get_connect_layout(self) -> List[List[Any]]:
        return [
            [
                sg.Text("RC: "),
                sg.Input('localhost', key="_input_ip_addr", size=32),
                sg.Input('9090', key="_input_port", size=5),
            ],
            [
                sg.Text("VD: "),
                sg.Input('http://192.168.0.6:9999/stream', key='_input_video_addr', size=38)
            ],
            [
                sg.Button("Connect", key="_button_connect"),
                sg.Text("Unable to connect", key="_text_error", visible=False)
            ],
        ]

    def get_op_layout(self) -> List[List[Any]]:
        return [
            [
                sg.Text('M: N/A', key="_text_mode"),
                sg.Text('SM: N/A', key="_text_sub_mode"),
                sg.Text('Speed: N/A', key="_text_speed"),
                sg.Text('L1: N/A', key="_text_light1"),
                sg.Text('L2: N/A', key="_text_light2"),
                sg.Text('Battery: N/A', key="_text_battery"),
            ],
            [
                sg.Image(key="_image_stream", visible =(not self.logs_view), size=self.IMG_SIZE),
                sg.Multiline('', size=(64,19), key="_multiline_log", autoscroll=True, visible=self.logs_view)
            ],
            [
                sg.Text("Connection quality: TBD"),
                sg.Button("Ping", key="_button_ping"),
                sg.Button("View: LOGS", key="_button_view"),
                sg.Button("Disconnect", key="_button_disconnect")
            ]
        ]


    def event_dispatcher(self, event: str, values: Optional[Dict[str,Any]]):
        if values is not None:
            self.ui_state = values.copy()
        if event in self.event_routes:
            self.event_routes[event]()


    def _button_connect(self):
        if not self.connected:
            host = self.ui_state["_input_ip_addr"]
            port = int(self.ui_state["_input_port"])
            video_addr =self.ui_state["_input_video_addr"]
            try:
                self.network_socket, self.network_client = connect(host, port)
            except TTransportException:
                self.unable_connect_count += 1
                self.window["_text_error"].update(f"Unable to connect {self.unable_connect_count}", visible=True)
                return
            self.unable_connect_count = 0
            self.connected = True
            logger.info("Connected to %s:%s", host, port)
            self.window.close()
            self.init_op_window()
            self.controller = SteamDeckController(self.network_client)
            self.video_stream = VideoStream(video_addr)
            if not self.logs_view:
                self.video_stream.enable()
        else:
            logger.warning("Already connected!")


    def _button_disconnect(self):
        if self.connected:
            self.controller.terminate()
            self.controller = None
            self.network_socket.close()
            self.network_client = None
            self.video_stream.disable()
            self.window.close()
            self.init_connect_window()
            self.connected = False
            logger.info("Disconnected")
        else:
            logger.warning("Already disconnected!")


    def _button_ping(self):
        if self.connected:
            self.network_client.ping()


    def _button_view(self):
        txt_map = {
            True: "LOGS",
            False: "VIDEO"
        }
        
        self.logs_view = not self.logs_view
        self.window["_multiline_log"].update(visible=self.logs_view)
        self.window['_image_stream'].update(visible=not self.logs_view)
        self.window["_button_view"].update("View: " + txt_map[self.logs_view])
        if self.logs_view:
            self.video_stream.disable()
        else:
            self.video_stream.enable()

    def update_op_values(self):
        if self.logs_view:
            while not self.controller.log_queue.empty():
                record = self.controller.log_queue.get()
                self.window['_multiline_log'].update(record+"\n", append=True)
        else:
            self.window['_image_stream'].update(data=self.video_stream.get_frame(), size=self.IMG_SIZE)

        robot_state = self.network_client.get_status()
        self.window["_text_mode"].update("M: " + Mode._VALUES_TO_NAMES[robot_state.mode])
        if robot_state.mode == Mode.WALK:
            self.window["_text_sub_mode"].update("SM: "+Giat._VALUES_TO_NAMES[robot_state.sub_mode])
        else:
            self.window["_text_sub_mode"].update("SM: NA")
        self.window["_text_speed"].update("speed: SLOW" if robot_state.speed == 1 else "speed: FAST")
        self.window["_text_light1"].update("L1: OFF" if robot_state.light_1 else "L1: ON")
        self.window["_text_light2"].update("L2: OFF" if robot_state.light_2 else "L2: ON")
        self.window["_text_battery"].update(f"Battery: {robot_state.battery}")

            
    def run(self):
        while True:
            event, values = self.window.read(timeout=100)
            self.event_dispatcher(event, values)
            if self.connected:
                self.update_op_values()
            self.window.refresh()
            if self.logs_view:
                time.sleep(0.05)


    def refresh(self):
        self.window.refresh()


    def read(self):
        return window.read()


    def close(self):
        window.close()
