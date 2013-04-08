#!/bin/bash
sudo mv /usr/bin/python3 /usr/bin/python3backup
sudo ln -s /opt/ActivePython-3.2/bin/python3.2 /usr/bin/python3
cd ./Setup/pyusb-1.0.0a3/
sudo python3 setup.py install
cd ..
cd ..
wget https://pypi.python.org/packages/source/p/pudb/pudb-2013.1.tar.gz
tar -xvf pudb-2013.1.tar.gz
cd pudb-2013.1
sudo python3 setup.py install
