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

* Use Git to clone the repository or you can directly download it
  by using the 'Download ZIP' button.  
  `$ git clone https://github.com/auriomalley/class-attendance-tracker.git`
  
* Change directory into the newly created **class-attendance-tracker**
  folder.  
  `$ cd class-attendance-tracker`

#### Raspberry Pi

I tested this with a Raspberry Pi model 4B 2GB RAM version with
Raspbian installed. I used the lite version of Raspbian but it
should work with other versions as well.

Before running the application we need to install some dependencies.
Running the below code installs some libraries needed by Pillow and
OpenCV.  
`$ sudo apt install libjpeg-dev libatlas-base-dev`  
We also need to install Python dependencies. You can also
install them using `pip`, but I recommend installing OpenCV the `apt` way
since it also installs needed libraries.  
`$ sudo apt install python3-pip python3-picamera python3-opencv opencv-data python3-pymongo`  
You can also use a virtual environment, but in that case you'll have to
hunt down all the needed dependencies on your own.
Lastly we need to install the rest of the Python libraries that are
not in the repositories.  
`$ sudo pip3 install pytz face_recognition tinydb`  
Now we are ready to run the application.  
`$ PYTHONPATH=./modules python3 RPI/main.py`  
`PYTHONPATH` part is important. Make sure you pass in the modules folder in
the project root. You can also create a script to run the application
for you.  
This first run will generate a `config.json` file in the `RPI/data` directory.
You can change your settings from there. Also you have to change `null`
values, otherwise application will raise error.

#### Client

Client will allow us to connect to the main server and the database,
so we can add students and receive reports. Client installation is simple.  

There are not many dependencies we need to install. We can use `pip` for that.
I also recommend using a virtual environment.  
`$ pip install pymongo pytz pandas`  
Then run the application.
`$ PYTHONPATH=./modules python3 client/main.py`  
After this first run you can change your config settings in the 
`client/data/config.json` file.
 
#### Server

Server allows us to connect the clients to the Raspberry Pis.  

`$ pip install pytz tinydb`  
You can use a virtual environment if you'd like to.  
Then run the application.
`$ PYTHONPATH=./modules python3 client/main.py`  
After this first run you can change your config settings in the 
`server/data/config.json` file.  
Application also requires a MongoDB database. I recommend using `docker` to
install the server. If you don't have it you can install it by following
this documentation https://docs.docker.com/install/linux/docker-ce/ubuntu/.  
`$ docker pull mongo`  
`$ docker run -d --network host
   -e MONGO_INITDB_ROOT_USERNAME=username
   -e MONGO_INITDB_ROOT_PASSWORD=password mongo`  
This will run a database.

***

How to use it?
--------------
After you installed the application, you can start by running the server.
Raspberry Pi doesn't run the code on startup so make sure you have that
set up, otherwise you'll have to connect to the Pi through `ssh` to start
the application every time. There is a tutorial on how to set it up
at https://www.raspberrypi.org/documentation/linux/usage/rc-local.md. Now
you can run the client application and start adding students.


