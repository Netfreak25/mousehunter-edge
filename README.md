![Catgate](docs/header.jpg)

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
Originally developed by [gerrito333 on Github](https://github.com/gerrito333/mousehunter-edge)
Keep your cat’s prey out of your home with a machine learning trained pet door.
Turn your Sureflap cat flap into a smart flap that locks when you cat tries to take prey into your home.
Leverage Google Coral Edge TPU to run millisecond inference on infrared images captured on your Raspberry Pi. Object detection is based on TFLite and a MobileNet v1 SSD.

[![Prey detections video](docs/video_thumb.png)](https://youtu.be/7k1KKuclu8M)
[Background story on Medium](https://link.medium.com/ZWStYOJhKcb)

> # Warning! The code in this repository is still in an early stage of development and will not work as it is. If you are looking for something that works I recommend the original repository from [gerrito333](https://github.com/gerrito333/mousehunter-edge) combined with the comments from [Tronje-the-Falconer](https://github.com/Tronje-the-Falconer/mousehunter-edge).

## The goal of this repository is to operate without motion detectors.

## Required hardware:

* [Sureflap](https://amzn.to/3mB8hc0) or [Sureflap Connect](https://amzn.to/3aFExbP)
* [Raspberry Pi 4B](https://amzn.to/2KiHtAl)
* [Raspberry USB Power supply](https://amzn.to/2LRrMAk)
* [Case for Raspberry](https://amzn.to/3nHltxb)
* [MicroSD Card](https://amzn.to/37IbhPM)
* [Google Coral](https://amzn.to/3aB5o8S)
* [Infrared camera](https://amzn.to/38tSWF4)
* [Camera cable](https://amzn.to/3mGkagM)
* [Jumper cables](https://amzn.to/3rkcYue)
* [Relay](https://amzn.to/38oLVpe)

## Setup Mausjaeger Service:

### update your Pi-OS
```bash
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y
```

### Enable Systemrequirements (Camera...
```bash
sudo raspi-config
```

### Install Google Coral TFLite Runtime and other dependencies
```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update && sudo apt install libedgetpu1-std python3-tflite-runtime git python3-picamera libtiff5 python3-pip
```

### Install Dependencies an compile OpenCV
The pip3-Package will not work on the RPi4, so you have do this yourself.
Grab a coffee, this will take some time...

#### Install Dependencies
````bash
sudo apt install cmake build-essential pkg-config git libjpeg-dev libtiff-dev libjasper-dev libpng-dev libwebp-dev libopenexr-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libdc1394-22-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libgtk-3-dev python3-pyqt5 libatlas-base-dev liblapacke-dev gfortran libhdf5-dev libhdf5-103-1 python3-dev python3-pip python3-numpy
````

#### enlarge swap before compiling
````bash
sudo nano /etc/dphys-swapfile
````

Change

> CONF_SWAPSIZE=100

to 

> CONF_SWAPSIZE=2048


Restart swap-Service
````bash
sudo systemctl restart dphys-swapfile
````

#### Get the latest version of OpenCV from GitHub.
````bash
cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
````

#### Create build dir and move into
````bash
mkdir ~/opencv/build
cd ~/opencv/build
````

#### Generate makefile and compile
````bash
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -D BUILD_EXAMPLES=OFF ..
	
make -j$(nproc)
sudo make install
sudo ldconfig
````

#### change swap back to original
````bash
sudo nano /etc/dphys-swapfile
````

Change

> CONF_SWAPSIZE=2048

to 

> CONF_SWAPSIZE=100


Restart swap-Service
````bash
sudo systemctl restart dphys-swapfile
````


### Install Python Dependencies
````bash
sudo pip3 install argparse
````

### Clone this repo on your raspberry
```bash
git clone https://github.com/de-wax/mousehunter-edge.git
```

### create image-folder
```bash
cd ~/mousehunter-edge/mausjaeger/
mkdir images
```

### Enable, start  and check Mausjaeger-Service
````bash
sudo systemctl enable ~/mousehunter-edge/mausjaeger/mausjaeger.service
sudo systemctl start mausjaeger.service
````

#### Check if service is running
````bash
systemctl status mausjaeger.service
````
also look at the log-File at: /var/log/mausjaeger.log

### Optional: Enable Log-Rotate for mausjaeger.log
````bash
sudo cp /home/pi/mousehunter-edge/mausjaeger/mausjaeger /etc/logrotate.d/mausjaeger
sudo systemctl restart logrotate
````




## Setup Imagewatcher Service


Install pypi for gpio support
```bash
pip3 install RPi.GPIO
```

install pinotify
```bash
pip3 install pyinotify
```

Install watchdog
```bash
pip3 install watchdog
```

Install boto3
```bash
pip3 install boto3
```

Install Pillow
```bash
pip3 install Pillow==2.2.2
```

Install APScheduler
```bash
pip3 install APScheduler
```

install confuse
```bash
pip3 install confuse
```

### Amazon support
install the AWS Command Line Interface
```bash
pip3 install awscli --upgrade --user
```

Add AWS CLI executable to your Command Line Path
```bash
export PATH=/home/pi/.localbin:$PATH
```

Configure the default AWS CLI
```bash
aws configure

AWS Access Key ID [None]: <<<YOUR_ACCESS_KEY_ID>>>
AWS Secret Access Key [None]: <<<YOUR_SECRET_ACCESS_KEY>>>
Default region name [None]: <<<YOUR_REGION_NAME_EXAMPLE_eu-central-1>>>
Default output format [None]: json
```

### Coral support
install the compiler 
```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
```
install Edge TPU runtime library
```bash
sudo apt-get install libedgetpu1-std
```

### Mousehunter 
Clone this repo on your raspberry
```bash
git clone https://github.com/gerrito333/mousehunter-edge.git
```
create image- and logfolder with logfile
```bash
cd mousehunter-edge/mausjaeger/
mkdir images
mkdir logs
cd logs
touch mausjaeger.log
```

### config mousehunter
copy config yaml to ~/.config/mousehunter-edge/
```bash
mkdir .config
cd .config
mkdir mousehunter-edge
cd ~/mousehunter-edge/imagewatcher
cp config.yaml ~/.config/mousehunter-edge/config.yaml
```

Connect motion detector OUT to GPIO8, check `pinout` to see your layout.

```
                                3V3  (1) (2)  5V         <--- motion detector VCC
                              GPIO2  (3) (4)  5V         <--- + port of relay
                              GPIO3  (5) (6)  GND        <--- motion detector GND
                              GPIO4  (7) (8)  GPIO14
                                GND  (9) (10) GPIO15
                              GPIO17 (11) (12) GPIO18
                              GPIO27 (13) (14) GND
                              GPIO22 (15) (16) GPIO23
                                 3V3 (17) (18) GPIO24
                              GPIO10 (19) (20) GND
                               GPIO9 (21) (22) GPIO25
                              GPIO11 (23) (24) GPIO8      <--- motion detector OUT
                                 GND (25) (26) GPIO7
                               GPIO0 (27) (28) GPIO1
                               GPIO5 (29) (30) GND
                               GPIO6 (31) (32) GPIO12
                              GPIO13 (33) (34) GND
                              GPIO19 (35) (36) GPIO16
     s-port of relay --->     GPIO26 (37) (38) GPIO20
     - port of relay --->        GND (39) (40) GPIO21
```


Configure  `~/.config/mousehunter-edge/config.yaml` with your AWS bucket name and ensure that aws credentials can read the objects in it.
Keep APNToken and certfile empty if you do not have it.

```bash
sudo nano ~/.config/mousehunter-edge/config.yaml
```

``` yaml
bucket: <<<YOUR_AWS_S3_BUCKET>>>
curfewTime: 15
APNToken: <<<YOUR_APPLE_PUSH_NOTIFICATION_SERVICE_APNs_TOKEN>>>
alertThreshold: 2.0
certfile: <<<YOUR_APPLE_CERTIFICATE_FOR_APN_FOR_APN_USAGE>>>
```

Update `WorkingDirectory` values for both .service files if not '/home/pi/mousehunter-edge/'.
```bash
sudo nano ~/mousehunter-edge/mausjaeger/mausjaeger.service
sudo nano ~/mousehunter-edge/imagewatcher/imagewatcher.service
```

```bash
sudo systemctl enable ~/mousehunter-edge/imagewatcher/imagewatcher.service
sudo systemctl start imagewatcher.service
```

Proove if services are running
```bash
systemctl status imagewatcher.service
```
## Retrain your own object detection model:

label you data with labelImg:
https://github.com/tzutalin/labelImg

Convert your labeled data to the TFRecord file format, e.g. with https://roboflow.com

Follow the coral.ai tuturials part "Set up the Docker container" on a machine with strong CPU. No GPU is required.
https://coral.ai/docs/edgetpu/retrain-detection/#set-up-the-docker-container

Copy your TFRecords to docker/object_detection/data

Configure train_input_reader, eval_input_reader and model.ssd.num_classes  the training pipeline:
```
docker/object_detection/out/ckpt/pipeline.config
```
Remove all lines following "PREPARING dataset" and execute the script:
```
docker/object_detection/scripts/prepare_checkpoint_and_dataset.sh
```

Contine to follow the coral.ai tutorial part "Start training" and "Compile the model for the Edge TPU"
Copy the created model to the imagewatcher/model/ folder.
..
