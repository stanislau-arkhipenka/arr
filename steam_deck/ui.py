import logging
import time
import PySimpleGUI as sg
from controller import SteamDeckController
from network import connect, Client
from typing import Any, Dict, List, Optional
import queue

logger = logging.getLogger(__name__)

class SteamDeckUI:

    def __init__(self):
        self.connected = False
        self.network_client: Client = None
        self._connect_layout = self.get_connect_layout()
        self._op_layout = self.get_op_layout()

        self.ui_state: Dict[str, Any] = {}

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
        self.window = sg.Window("Connect", self._connect_layout, finalize=True)
    
    def init_op_window(self):
        self._op_layout = self.get_op_layout()
        self.window = sg.Window("Operational Panel", self._op_layout, finalize=True)

    def get_connect_layout(self) -> List[List[Any]]:
        return [
            [
                sg.Input('localhost', key="_input_ip_addr"),
                sg.Input('9090', key="_input_port"),
                sg.Button("Connect", key="_button_connect"),
            ],
        ]

    def get_op_layout(self) -> List[List[Any]]:
        self._multiline_log = sg.Multiline('', size=(50,25), key="_multiline_log", autoscroll=True)
        return [
            [
                sg.Text('M: N/A'),
                sg.Text('SM: N/A'),
                sg.Text('Speed: N/A'),
                sg.Text('L1: N/A'),
                sg.Text('L2: N/A'),
                sg.Text('Battery: N/A'),
            ],
            [
                # TODO insert image here
                self._multiline_log
            ],
            [
                sg.Text("Connection: Stable"),
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
