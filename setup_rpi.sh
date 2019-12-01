#!/bin/bash
echo "Updating the packages"
sudo apt update
sudo apt upgrade -y
echo "Installing necessary packages"
sudo apt install git
sudo apt install libjpeg-dev libatlas-base-dev
sudo apt install python3-pip python3-picamera python3-opencv opencv-data python3-pymongo
sudo pip3 install pytz face_recognition tinydb
echo "Downloading the project files"
git clone https://github.com/auriomalley/class-attendance-tracker.git
echo "Performing necessary configurations"
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

echo "#!/bin/bash
cd ${project_root}/RPI/main
PYTHONPATH=${project_root}/modules python3 ${project_root}/RPI/main/rpi_main.py" > run_rpi.sh

chmod +x run_rpi.sh

echo "Installation is complete. Please go to ${project_root}/RPI/data/config and fill in the json files."
echo "You can run the application by executing run_rpi.sh file."
