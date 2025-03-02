# pi-birdcam

This is a project, based on an article https://www.raspberry-pi-geek.de/ausgaben/rpg/2017/10/nistkaesten-mit-der-pi-cam-ins-internet-bringen/ 
to create a bird-cam with a raspberry-pi.

I'm using
* Raspberry-Pi 3+
* Camera V2.1 (Infrared cam for raspberry pi)
* An Infrared LED
* WiFi USB-Dongle

I've built a wooden bird-house with a double back and attached the bird-cam and LED on the roof.

## Installation

1. Setup you raspberry-pi with an [raspbian-light installation](https://www.raspberrypi.com/software/).

2. Download the github-repo onto your raspberry

3. Setup the RAM-Disk

```sh
# create ramdisk
sudo mkdir /mnt/ramdisk

# edit the fstab
sudo nano /etc/fstab
```
edit the fstab and insert following contents
```sh
tmpfs /mnt/ramdisk tmpfs nodev,nosuid,size=64M 0 0
```

4. install picam

```sh
# setup virtual environment
python3 -m venv my-venv
# install python picamera
sudo apt install -y python3-picamera2 python3-libcamera
```

5. test the camera by executing 

```sh
./testcam.py
```

download the picture and check if it's working

## Upload
instead of a custom server I'm using a drop-file directory in Nextcloud.
Just use an own or hosted instance of a nextcloud and make the directory available.

## Run automatically

to run that automatically and repeatedly edit the crontabs

`crontab -e`

```sh
# Alle 15 Sekunden ein Bild aufnehmen und hochladen
* * * * * sleep 0; /home/froeser/pi-birdcam/meisencam.py >/dev/null 2>&1
* * * * * sleep 15; /home/froeser/pi-birdcam/meisencam.py >/dev/null 2>&1
* * * * * sleep 30; /home/froeser/pi-birdcam/meisencam.py >/dev/null 2>&1
* * * * * sleep 45; /home/froeser/pi-birdcam/meisencam.py >/dev/null 2>&1
```

and since the raspberry pi sometimes needs a restart, add this:

`sudo crontab -e`

```sh
0 0 * * * /sbin/shutdown -r
```