#!/bin/bash
echo "Updating the packages"
sudo apt update
sudo apt upgrade
echo "Installing necessary packages"
sudo apt install git
sudo apt install python3-pip
pip3 install tinydb 
echo "Downloading the project files"
git clone https://github.com/auriomalley/class-attendance-tracker.git
echo "Performing necessary configurations"
cd class-attendance-tracker/server
mkdir data
mkdir data/users

echo '{
  "_default": {
    "1": {
      "username": "",
      "password": ""
    }
  }
}' > data/users/db.json

cd ..

project_root=$(pwd)

echo "#!/bin/bash
cd ${project_root}/server/main
PYTHONPATH=${project_root}/modules python3 ${project_root}/server/main/server_main.py" > run_server.sh

chmod +x run_server.sh

echo "Installation is complete. Please add users in ${project_root}/server/data/users/db.json."
echo "You can run the application by executing run_server.sh file."
