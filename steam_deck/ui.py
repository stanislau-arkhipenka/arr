# hello_psg.py
import logging
import time
import PySimpleGUI as sg
from controller import SteamDeckController
from network import connect, Client
from typing import Any, Dict

logger = logging.getLogger(__name__)

class SteamDeckUI:

    def __init__(self):
        self.connected = False
        self.network_client: Client = None
        self._connect_layout = self.get_screen_connect()
        self._operate_layout = []

        self.window = sg.Window("Demo", self._connect_layout, finalize=True)
        self.ui_state: Dict[str, Any] = {}


        self.event_routes = {
            "_button_connect": self._button_connect
        }


    def get_screen_connect(self):
        self._connect_layout = [
            [
                sg.Input('hexapod', key="_input_ip_addr"),
                sg.Input('9090', key="_input_port"),
                sg.Button("Connect", key="_button_connect"),
            ],
        ]
        
        return self._connect_layout

    def screen_operate(self):
        pass


    def event_dispatcher(self, event: str, values: Dict[str,Any]):
        logger.debug("%s -- %s", event, values)
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
        else:
            logger.info("ping!")
            self.network_client.ping()


    def run(self):
        while True:
            event, values = self.window.read()
            self.event_dispatcher(event, values)
            
            self.window.refresh()
            time.sleep(0.05)


    def update_op_values(self, values):
        pass

    def refresh(self):
        self.window.refresh()

    def read(self):
        return window.read()

    def close(self):
        window.close()
