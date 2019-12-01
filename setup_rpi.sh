#!/bin/bash
sudo apt update
sudo apt upgrade -y
sudo apt install git
sudo apt install libjpeg-dev libatlas-base-dev
sudo apt install python3-pip python3-picamera python3-opencv python3-pymongo
sudo pip3 install pytz face_recognition tinydb
git clone https://github.com/auriomalley/class-attendance-tracker.git
cd class-attendance-tracker/RPI
mkdir data
mkdir data/config

echo '{                                        
  "username": "",
  "password": "",
  "host": "",
  "port": 0
}' > data/config/central_server_connection.json

echo '{
  "pi-id": "",
  "location": ""
}' > data/config/pi.json

echo '{                                        
  "timezone": "",
  "sub-name": ""
}' > data/config/project.json

echo '{                                        
  "username": "",
  "password": "",
  "host": "",
  "port": 0
}' > data/config/remote_mongo_connection.json

cd ..

project_root=$(pwd)

echo "PYTHONPATH=${project_root}/modules python3 ${project_root}/RPI/main/rpi_main.py" > run_rpi.sh
