#!/usr/bin/python3
# meisencam.py
# Bildveränderungserkennung mit PIL und PiCamera2

from picamera2 import Picamera2
import time
from pathlib import Path
import requests
from PIL import Image
import logging
from datetime import datetime
import shutil

class MeisenCam:
    BASE_URL = "https://pro.woelkli.com/s/Gi2bRAHrgMoebcA"

    def __init__(self):
        # Voreinstellungen
        self.WIDTH = 320
        self.HEIGHT = 240
        self.SCHWELLWERT = 1.0
        self.RAMDISK_PATH = Path('/mnt/ramdisk')
        self.current_image_path = self.RAMDISK_PATH / 'meisencam.jpg'
        self.old_image_path = self.RAMDISK_PATH / 'meisencamalt.jpg'
        self.log_path = self.RAMDISK_PATH / 'meisencam.log'
        
        # Logging konfigurieren
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s'
        )

        # Initialisierungskonfigurationen loggen
        logging.info("Initialisiere MeisenCam mit folgenden Einstellungen:")
        logging.info(f"Bildbreite: {self.WIDTH}px")
        logging.info(f"Bildhöhe: {self.HEIGHT}px") 
        logging.info(f"Bewegungsschwellwert: {self.SCHWELLWERT}")
        logging.info(f"RAM-Disk Pfad: {self.RAMDISK_PATH}")
        
        # Kamera initialisieren
        self.camera = Picamera2()
        # Kurz warten bis Kamera bereit ist
        time.sleep(1)
        logging.info("camera created, now set configurations")
        self.configure_camera()
        logging.info("camera configured successfully")
        
    def configure_camera(self):
        """Konfiguriert die Kamera mit den gewünschten Einstellungen"""
        config = self.camera.create_still_configuration(
            main={"size": (self.WIDTH, self.HEIGHT)}
        )
        self.camera.configure(config)
        # Automatische Belichtungssteuerung aktivieren
        self.camera.set_controls({
            "AeEnable": True,  # Automatische Belichtung aktivieren
            "AeMeteringMode": 0,  # Durchschnittliche Belichtungsmessung
            "AeConstraintMode": 0,  # Normal
            "AeExposureMode": 0,  # Normal
            "AwbMode": 2,  # Cloudy
            "Brightness": 0.6  # 60%
        })
        logging.info("Automatische Belichtungssteuerung aktiviert")
        
    def capture_image(self):
        """Nimmt ein Bild auf und speichert es"""
        self.camera.start()
        time.sleep(2)  # Wartezeit für Sensor-Stabilisierung
        
        zeitstempel = datetime.now().strftime("%Y%m%d-%H%M%S")
        metadata = self.camera.capture_file(str(self.current_image_path))
        
        self.camera.stop()
        return zeitstempel
        
    def calculate_movement(self):
        """Berechnet die Bewegungskennzahl zwischen zwei aufeinanderfolgenden Bildern.
        Die Kennzahl repräsentiert den durchschnittlichen Unterschied der Pixelwerte zwischen den Bildern.
        Ein höherer Wert deutet auf mehr Bewegung hin.
        
        Wenn die Kennzahl > SCHWELLWERT (35) ist, wird das Bild als Bewegung erkannt (mode=1).
        Wenn die Kennzahl <= SCHWELLWERT ist, wird keine Bewegung erkannt (mode=0).
        
        Returns:
            float: Bewegungskennzahl zwischen 0 (keine Änderung) und 255 (maximale Änderung)
        """
        try:
            bildneu = Image.open(self.current_image_path).convert("L")
            bildalt = Image.open(self.old_image_path).convert("L")
        except FileNotFoundError:
            # Falls kein altes Bild existiert
            logging.info("No old image found, copying current image as old image")
            shutil.copy2(str(self.current_image_path), str(self.old_image_path))
            return 0
            
        # Bilder verkleinern für Vergleich
        logging.info("resizing images for movement detection")
        size = (4, 3)
        bildneu = bildneu.resize(size)
        bildalt = bildalt.resize(size)
        
        # Kennzahl berechnen
        differenz = 0
        for x in range(size[0]):
            for y in range(size[1]):
                differenz += abs(bildneu.getpixel((x,y)) - bildalt.getpixel((x,y)))
                
        kennzahl = differenz / (size[0] * size[1])
        
        # Altes Bild durch aktuelles Bild ersetzen (kopieren statt umbenennen)
        shutil.copy2(str(self.current_image_path), str(self.old_image_path))
        
        return kennzahl
    
    def upload_image(self, mode):
        """example valid curl: curl -v -k -T meisencam.jpg -u 'folderid:' https://pro.woelkli.com/public.php/webdav/001.jpg"""
        """Lädt das Bild zum Nextcloud WebDAV hoch wenn Bewegung erkannt wurde (mode=1)"""
        # if mode != 1:
        #     logging.info(f"Keine Bewegung erkannt (mode={mode}), überspringe Upload")
        #     return None
            
        zeitstempel = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        zieldatei = f"{zeitstempel}-m{mode}.jpg"
        url = f"https://pro.woelkli.com/public.php/webdav/{zieldatei}"
        auth = ('Gi2bRAHrgMoebcA', '')  # Username und leeres Passwort
        
        logging.info(f"Versuche Bild hochzuladen: {self.current_image_path} nach: {url}")
        try:
            with open(self.current_image_path, 'rb') as img:
                response = requests.put(url, data=img, auth=auth, verify=False)
                logging.info(f"Upload Antwort: {response.status_code}")
                return response
        except FileNotFoundError:
            logging.error(f"Konnte Datei {self.current_image_path} nicht zum Upload finden")
            return None
        
    def log_activity(self, zeitstempel, kennzahl, mode, response):
        """Protokolliert die Aktivität"""
        log_entry = f"{zeitstempel};{kennzahl};{mode};{response.text}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)
            
    def run(self):
        """Hauptprozess"""
        logging.info("executing capture_image()")
        zeitstempel = self.capture_image()
        logging.info("executing calculate_movement()")
        kennzahl = self.calculate_movement()
        mode = 1 if kennzahl > self.SCHWELLWERT else 0
        
        logging.info(f"Zeitstempel: {zeitstempel}")
        logging.info(f"Kennzahl: {kennzahl}")
        logging.info(f"Modus: {mode}")
        
        logging.info("executing upload_image()")
        response = self.upload_image(mode)
        self.log_activity(zeitstempel, kennzahl, mode, response)

if __name__ == "__main__":
    try:
        cam = MeisenCam()
        cam.run()
    except Exception as e:
        logging.error(f"Fehler: {str(e)}")
