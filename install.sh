#!/bin/bash

sudo ln -s $(pwd) /opt/arr
python3 -m virtualenv -p python3 /opt/arr/.venv
ln -s /opt/arr/acp /opt/arr/.venv/lib/python3.7/site-packages/acp
source /opt/arr/.venv/bin/activate
pip3 install -r requirements.txt
sed "s/MY_USER/$USER/g" example_hexapod.service > hexapod.service
sudo mv ./hexapod.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable hexapod.service
