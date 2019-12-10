Class Attendance Tracker
========================
This is my first big project so the code is a little messy! Also,
I don't have the habit of commenting my code, so there is that.

The goal of this project is to automate tracking students
by recognizing their faces. When a student enters to a class,
the camera (a Raspberry Pi in this case) recognizes their faces
and keeps a record of this in a database. Later we can find
who attended the class by analyzing these records.

Currently, it is at a very early stage of development, so there
are not many features.

We need at least 3 devices (a client, a camera and a server)
to run this application. Server's purpose is to create a connection
point between clients and cameras. Client application is where we'll
connect to cameras and change their settings.

***

Installation
------------

The steps below will take you through installing the application.  
**Note:** This is only tested in Linux, so if you are using MacOS
or Windows it may not work properly.

* Use Git to clone the repository or you can directly download it
  by using the 'Download ZIP' button.  
  `$ git clone https://github.com/auriomalley/class-attendance-tracker.git`
  
* Change directory into the newly created _class-attendance-tracker_
  folder.  
  `$ cd class-attendance-tracker`

#### Raspberry Pi

I tested this with a Raspberry Pi model 4B 2GB RAM version with
Raspbian installed. I used the lite version of Raspbian but it
should work with other versions as well.

* Install dependencies required for Pillow and OpenCV.  
  `$ sudo apt install libjpeg-dev libatlas-base-dev`  
  
* Install Python dependencies. You can use Pip with a virtual environment,
  but I recommend doing it the Apt way since it also installs some needed
  libraries.   
  `$ sudo apt install python3-pip python3-picamera python3-opencv opencv-data python3-pymongo`  
  **Note:** If you choose to do it using a virtual environment and Pip you
  may have to hunt down all other needed libraries on your own.
  
* Install the libraries that are not available in the repositories using Pip.   
  `$ sudo pip3 install pytz face_recognition tinydb`  

* Run the application.  
  `$ PYTHONPATH=./modules python3 RPI/main.py`  
  **Note:** Setting _PYTHONPATH_ correctly is really important. It
  should point to the _modules_ folder in the _class-attendance-tracker_
  folder, otherwise it won't work since I haven't figured out an elegant 
  way of managing it.

* This first run will generate a _config.json_ file in the _RPI/data_
  directory. Go there and change the config settings.  
  **Note:** If there are any _null_ values in the config file, application
  will raise an error.

#### Client

Client will allow us to connect to the main server and the database,
so we can add students and receive reports. Installation is pretty straightforward.  

* Install needed dependencies.  
  `$ pip3 install pymongo pytz`  
  **Note:** I recommend using a virtual environment since there are
  no packages that would cause trouble later.

* Run the application.  
  `$ PYTHONPATH=./modules python3 client/main.py`  
  **Note:** Setting _PYTHONPATH_ correctly is really important. It
  should point to the _modules_ folder in the _class-attendance-tracker_
  folder, otherwise it won't work since I haven't yet figured out an elegant 
  way of managing it.

* This first run will generate a _config.json_ file in the _client/data_
  directory. Go there and change the config settings.  
  **Note:** If there are any _null_ values in the config file, application
  will raise an error.
 
#### Server

Server allows us to connect the clients to the Raspberry Pis.

* Install needed dependencies.  
  `$ pip3 install tinydb pytz`  
  **Note:** I recommend using a virtual environment since there are
  no packages that would cause trouble later.

* Run the application.  
  `$ PYTHONPATH=./modules python3 server/main.py`  
  **Note:** Setting _PYTHONPATH_ correctly is really important. It
  should point to the _modules_ folder in the _class-attendance-tracker_
  folder, otherwise it won't work since I haven't yet figured out an elegant 
  way of managing it.

* This first run will generate a _config.json_ file in the _server/data_
  directory. Go there and change the config settings.  
  **Note:** If there are any _null_ values in the config file, application
  will raise an error.
 
* This application also requires a MongoDB database. I recommend using
  _docker_ to install the MongoDB server. If you don't have it you can
   install it by following this documentation:
   [Docker CE Installation](https://docs.docker.com/install/linux/docker-ce/ubuntu/). 
    
  `$ docker pull mongo`  
  `$ docker run -d --network host
     -e MONGO_INITDB_ROOT_USERNAME=username
     -e MONGO_INITDB_ROOT_PASSWORD=password mongo`  

  This will run the database.a

***

How to use it?
--------------
After you installed the application, you can start by running the server.
Raspberry Pi doesn't run the code on startup so make sure you have that
set up, otherwise you'll have to connect to the Pi through `ssh` to start
the application every time. There is a tutorial on how to set it up:
[Run command on boot](https://www.raspberrypi.org/documentation/linux/usage/rc-local.md).
Now you can run the client application and start adding students.
