# hello_psg.py

import PySimpleGUI as sg


input_ip_addr = sg.Input('192.168.0.1')
button_connect = sg.Button("Connect")
layout = [
    [input_ip_addr, button_connect], 
    []
]

# Create the window
window = sg.Window("Demo", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()
