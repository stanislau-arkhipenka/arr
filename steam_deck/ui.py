import logging
import time
import PySimpleGUI as sg
from controller import SteamDeckController
from network import connect, Client
from typing import Any, Dict, List, Optional
from spec.ttypes import ARR_status, Mode, Giat
import queue

logger = logging.getLogger(__name__)

class SteamDeckUI:

    FONT = ("Arial", 22)

    def __init__(self):
        self.connected = False
        self.network_client: Client = None
        self._connect_layout = self.get_connect_layout()
        self._op_layout = self.get_op_layout()

        self.ui_state: Dict[str, Any] = {}
        self.robot_state = ARR_status(
            mode = 0,
            sub_mode = 0,
            speed = 0,
            light_1 = False,
            light_2 = False,
            battery = 0,
        )

        self.init_connect_window()
        self.event_routes = {
            "_button_connect": self._button_connect,
            "_button_disconnect": self._button_disconnect,
            "_button_ping": self._button_ping
        }

        self._multiline_log = None
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
                sg.Input('localhost', key="_input_ip_addr", size=32),
                sg.Input('9090', key="_input_port", size=5),
            ],
            [
                sg.Button("Connect", key="_button_connect"),
            ],
        ]

    def get_op_layout(self) -> List[List[Any]]:
        self._multiline_log = sg.Multiline('', size=(64,18), key="_multiline_log", autoscroll=True)
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
                # TODO insert image here
                self._multiline_log
            ],
            [
                sg.Text("Connection quality: TBD"),
                sg.Button("Ping", key="_button_ping"),
                sg.Button("Video: OFF"),
                sg.Button("Logs: OFF"),
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
            self.network_client = connect(host, port)
            self.connected = True
            logger.info("Connected to %s:%s", host, port)
            self.window.close()
            self.init_op_window()
            self.controller = SteamDeckController(self.network_client)
        else:
            logger.warning("Already connected!")

    def _button_disconnect(self):
        if self.connected:
            # TODO do disconnect logic here! Close Socket/etc
            self.window.close()
            self.init_connect_window()
            self.connected = False
            logger.info("Disconnected")
        else:
            logger.warning("Already disconnected!")

    def _button_ping(self):
        if self.connected:
            self.network_client.ping()

    def update_op_values(self):
        while not self.controller.log_queue.empty():
            record = self.controller.log_queue.get()
            self.window['_multiline_log'].update(record+"\n", append=True)
        self.robot_state = self.network_client.get_status()
        self.window["_text_mode"].update("M: " + Mode._VALUES_TO_NAMES[self.robot_state.mode])
        if self.robot_state.mode == Mode.WALK:
            self.window["_text_sub_mode"].update("SM: "+Giat._VALUES_TO_NAMES[self.robot_state.sub_mode])
        else:
            self.window["_text_sub_mode"].update("SM: NA")
        self.window["_text_speed"].update("speed: SLOW" if self.robot_state.speed == 1 else "speed: FAST")
        self.window["_text_light1"].update("L1: OFF" if self.robot_state.light_1 else "L1: ON")
        self.window["_text_light2"].update("L2: OFF" if self.robot_state.light_2 else "L2: ON")
        self.window["_text_battery"].update(f"Battery: {self.robot_state.battery}")

            
    def run(self):
        while True:
            event, values = self.window.read(timeout=100)
            self.event_dispatcher(event, values)
            if self.connected:
                self.update_op_values()
            self.window.refresh()
            time.sleep(0.05)


    def refresh(self):
        self.window.refresh()

    def read(self):
        return window.read()

    def close(self):
        window.close()
