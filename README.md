![Catgate](docs/header.jpg)

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

Keep your cat’s prey out of your home with a machine learning trained pet door.
Turn your Sureflap cat flap into a smart flap that locks when you cat tries to take prey into your home.
Leverage Google Coral Edge TPU to run millisecond inference on infrared images captured on your Raspberry Pi. Object detection is based on TFLite and a MobileNet v1 SSD.

[![Prey detections video](docs/video_thumb.png)](https://youtu.be/7k1KKuclu8M)
[Background story on Medium](https://link.medium.com/ZWStYOJhKcb)

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
* [Motion detector](https://amzn.to/3aB6nWC)
* [Relay](https://amzn.to/38oLVpe)

## Setup:

update your Pi-OS
```bash
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get dist-upgrade
```

Enable Systemrequirements (Camera...
```bash
sudo raspi-config
```
install git
```bash
sudo apt-get install git
```

install pip3
```bash
sudo apt-get install python3-pip
```

Clone this repo on your raspberry
```bash
git clone https://github.com/gerrito333/mousehunter-edge.git
```

Install pypi for gpio support
```bash
pip3 install RPi.GPIO
```

Install picamera
```bash
sudo apt-get install python-picamera python3-picamera
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

Install libtiff5
```bash
sudo apt install libtiff5
```

Install tflite runtime
```bash
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install python3-tflite-runtime
```

Install APScheduler
```bash
pip3 install APScheduler
```

install confuse
```bash
pip3 install confuse
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

### Amazon support
install the AWS Command Line Interface
```bash
pip3 install awscli --upgrade --user
```

Add AWS CLI executable to your Command Line Path
```bash
export PATH=/home/pi/.local/bin:$PATH
```

Configure the default AWS CLI
```bash
aws configure

AWS Access Key ID [None]: <<<YOUR_ACCESS_KEY_ID>>>
AWS Secret Access Key [None]: <<<YOUR_SECRET_ACCESS_KEY>>>
Default region name [None]: <<<YOUR_REGION_NAME_EXAMPLE_eu-central-1>>>
Default output format [None]: json
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
sudo systemctl enable ~/mousehunter-edge/mausjaeger/mausjaeger.service
sudo systemctl enable ~/mousehunter-edge/imagewatcher/imagewatcher.service
sudo systemctl start mausjaeger.service
sudo systemctl start imagewatcher.service
```

Proove if services are running
```bash
systemctl status mausjaeger.service
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
