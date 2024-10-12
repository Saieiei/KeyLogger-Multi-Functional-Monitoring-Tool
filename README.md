This project is a Python-based keylogger with additional features designed to capture comprehensive system activities. It includes:

Keyboard and Mouse Monitoring: Logs all key presses and mouse movements (including clicks and scrolls).
Active Window Tracking: Continuously records the currently active window, along with periodic screenshots.
System Information: Logs details such as the system hostname, IP address, processor, and OS information.
Microphone Recording: Periodically records audio from the microphone and saves it as a .wav file.
Camera Recording: Captures video from the webcam, saving it as an .avi file.
Screenshot Capturing: Takes screenshots at regular intervals to monitor screen activity.
Automated Email Reporting: Packages all collected data into a zip file and sends it to a pre-defined email address for remote access.
File Compression: Zips all log files, screenshots, sound recordings, and videos for easier email reporting.
Cross-Platform Compatibility: The keylogger is designed to run on Windows and other platforms, leveraging popular libraries like pynput, cv2, and pyscreenshot.
