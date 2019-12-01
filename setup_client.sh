#!/bin/bash
echo "Updating the packages"
sudo apt update
sudo apt upgrade -y
echo "Installing necessary packages"
sudo apt install git
sudo apt install python3-pip python3-pandas python3-pymongo
echo "Downloading the project files"
git clone https://github.com/auriomalley/class-attendance-tracker.git
echo "Performing necessary configurations"
cd class-attendance-tracker/client
mkdir data
mkdir data/config

echo '{
  "username": "",
  "password": "",
  "host": "",
  "port": 0
}' > data/config/central_server_connection.json

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
cd ${project_root}/client/main
PYTHONPATH=${project_root}/modules python3 ${project_root}/client/main/client_main.py" > run_client.sh

chmod +x run_client.sh

echo "Installation is complete. Please go to ${project_root}/client/data/config and fill in the json files."
echo "You can run the application by executing run_client.sh file."
