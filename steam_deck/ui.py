# hello_psg.py

import PySimpleGUI as sg

class SteamDeckUI:

    def __init__(self):
        self.window = sg.Window("Demo", layout)
        self._connect_layout = []
        self._operate_layout = []


    def screen_connect(self):
        self._connect_layout = [
            [
                sg.Input('192.168.0.1', key="_input.ip_addr"),
                sg.Button("Connect", key="_button.connect"),
            ],
        ]
        
        layout = [[sg.Text("Hello from PySimpleGUI")], [sg.Button("OK")]]

    def screen_operate(self):
        pass

    def update_op_values(self, values):
        pass

    def refresh(self):
        self.window.refresh()

    def read(self):
        return window.read()

    def close(self):
        window.close()
