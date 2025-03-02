#!/usr/bin/python3
# meisencam.py
# Bildveränderungserkennung mit PIL und PiCamera2

from picamera2 import Picamera2
from picamera2.transforms import Transform
import time
from pathlib import Path
import requests
from PIL import Image
import logging
from datetime import datetime

class MeisenCam:
    BASE_URL = "https://pro.woelkli.com/s/Gi2bRAHrgMoebcA"

    def __init__(self):
        # Voreinstellungen
        self.WIDTH = 320
        self.HEIGHT = 240
        self.SCHWELLWERT = 35
        self.RAMDISK_PATH = Path('/mnt/ramdisk')
        self.current_image_path = self.RAMDISK_PATH / 'meisencam.jpg'
        self.old_image_path = self.RAMDISK_PATH / 'meisencamalt.jpg'
        self.log_path = self.RAMDISK_PATH / 'meisencam.log'
        
        # Logging konfigurieren
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )
        
        # Kamera initialisieren
        self.camera = Picamera2()
        self.configure_camera()
        
    def configure_camera(self):
        """Konfiguriert die Kamera mit den gewünschten Einstellungen"""
        config = self.camera.create_still_configuration(
            main={"size": (self.WIDTH, self.HEIGHT)},
            transform=Transform(hflip=False, vflip=False)
        )
        self.camera.configure(config)
        
        # Kamera-Einstellungen
        self.camera.set_controls({
            "AnalogueGain": 4.0,  # ISO 400 equivalent
            "ExposureTime": 25000,
            "AwbMode": 2,  # Cloudy
            "Brightness": 0.6  # 60%
        })
        
    def capture_image(self):
        """Nimmt ein Bild auf und speichert es"""
        self.camera.start()
        time.sleep(2)  # Wartezeit für Sensor-Stabilisierung
        
        zeitstempel = datetime.now().strftime("%Y%m%d-%H%M%S")
        metadata = self.camera.capture_file(str(self.current_image_path))
        
        self.camera.stop()
        return zeitstempel
        
    def calculate_movement(self):
        """Berechnet die Bewegungskennzahl zwischen zwei Bildern"""
        try:
            bildneu = Image.open(self.current_image_path).convert("L")
            bildalt = Image.open(self.old_image_path).convert("L")
        except FileNotFoundError:
            # Falls kein altes Bild existiert
            self.current_image_path.rename(self.old_image_path)
            return 0
            
        # Bilder verkleinern für Vergleich
        size = (4, 3)
        bildneu = bildneu.resize(size)
        bildalt = bildalt.resize(size)
        
        # Kennzahl berechnen
        differenz = 0
        for x in range(size[0]):
            for y in range(size[1]):
                differenz += abs(bildneu.getpixel((x,y)) - bildalt.getpixel((x,y)))
                
        kennzahl = differenz / (size[0] * size[1])
        
        # Aktuelles Bild als altes Bild speichern
        self.current_image_path.rename(self.old_image_path)
        
        return kennzahl
        
    def upload_image(self, mode):
        """Lädt das Bild zum Webserver hoch"""
        base_url = self.BASE_URL  # Defined as class constant
        url = f"{base_url}?mode=1" if mode else base_url
        
        with open(self.current_image_path, 'rb') as img:
            files = {'file': img}
            response = requests.post(url, files=files)
            
        return response
        
    def log_activity(self, zeitstempel, kennzahl, mode, response):
        """Protokolliert die Aktivität"""
        log_entry = f"{zeitstempel};{kennzahl};{mode};{response.text}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
            
    def run(self):
        """Hauptprozess"""
        zeitstempel = self.capture_image()
        kennzahl = self.calculate_movement()
        mode = 1 if kennzahl > self.SCHWELLWERT else 0
        
        logging.info(f"Zeitstempel: {zeitstempel}")
        logging.info(f"Kennzahl: {kennzahl}")
        logging.info(f"Modus: {mode}")
        
        response = self.upload_image(mode)
        self.log_activity(zeitstempel, kennzahl, mode, response)

if __name__ == "__main__":
    try:
        cam = MeisenCam()
        cam.run()
    except Exception as e:
        logging.error(f"Fehler: {str(e)}")
