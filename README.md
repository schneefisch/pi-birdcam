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

4. Install dependencies

```sh
# install picamera2 system package (cannot be installed via pip on aarch64)
sudo apt install -y python3-picamera2 python3-libcamera

# create venv with access to system site-packages (required for picamera2)
uv venv --system-site-packages

# install project dependencies
uv sync
```

5. Test the camera by taking a single picture

```sh
uv run python -m meisencam --test
```

This captures one image to `/mnt/ramdisk/meisencam.jpg` and exits. You can specify a custom output path:

```sh
uv run python -m meisencam --test --output /tmp/test.jpg
```

> **Note:** Always use `uv run` to execute commands so that the virtual environment is used automatically. Alternatively, activate the venv first with `source .venv/bin/activate`.

Download the picture and check if it's working.

## Upload
instead of a custom server I'm using a drop-file directory in Nextcloud.
Just use an own or hosted instance of a nextcloud and make the directory available.

## Run automatically

to run that automatically and repeatedly edit the crontabs

`crontab -e`

```sh
# Alle 2 Minuten ein Bild aufnehmen und hochladen
*/2 * * * * cd /home/froeser/pi-birdcam && uv run python -m meisencam >/dev/null 2>&1
```

and since the raspberry pi sometimes needs a restart, add this:

`sudo crontab -e`

```sh
0 0 * * * /sbin/shutdown -r
```