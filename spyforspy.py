from PIL.Image import new
import numpy as np
import pyautogui
import itertools
import cv2
import time
from PIL import Image
import smtplib
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import imaplib
import email
from email.header import decode_header

def img_to_vector(img):
    pixels = list(img.getdata())
    colors = list(itertools.chain(*pixels))
    return colors

# setting smtp in advance
print("starting....")
s = smtplib.SMTP(host="smtp.gmail.com", port=587 or 465)
s.starttls()
BY = "****"
TO = "****"
PASS = "****"
s.login(BY, PASS)
imap = imaplib.IMAP4_SSL(host='imap.gmail.com',port=993)
imap.login(BY, PASS)
# marker email structure -> used to block the old commands from the inbox  
MARK_SUB = "marker"
marker_body = "marker"
mark = MIMEMultipart()
mark['From'] = BY
mark['To'] = BY
mark['Subject'] = MARK_SUB
mark.attach(MIMEText(marker_body,'plane'))
main_screen = pyautogui.screenshot()
count = 2
s.send_message(mark)
target = img_to_vector(main_screen)
print("Setup complete")


def check_screen():
    global target
    check = pyautogui.screenshot()
    check = img_to_vector(check)
    score = 0
    for i in range(0,len(check)):
        if target[i] == check[i]:
            score += 1
    score = (score/len(check))*100
    return score, check

def vec_to_image(colors, img):
    width, height = img.size
    img_bytes = bytes(colors)
    im = Image.frombytes("RGB", (width, height), img_bytes)
    return im

def run():
    print("System sequrity started BOSS, you can leave it to me now")
    global target
    global count
    while True:
        maching_percent, new_target = check_screen() 
        if maching_percent < 96:
            print('Intruder Detected') # other actions
            camera = cv2.VideoCapture(0)
            return_value, image = camera.read()
            cv2.imwrite('intruder#'+str(count-1)+'.png', image)
            ss = vec_to_image(new_target, main_screen)
            ss.save('screen#'+str(count-1)+'.png')
            del(camera)
            count += 1 
        target = new_target
        time.sleep(1)
        if count%3 == 0:
            send_intruder_detail()
        try:    
            cmd = get_command()
            if 'shut down' in str(cmd).lower():
                s.send_message(mark)
                os.system('shutdown -s')  
            elif 'warn' in str(cmd).lower():
                s.send_message(mark)
                os.system("notepad.exe warning.txt")
            elif 'from boss >>' in str(cmd).lower():
                s.send_message(mark)
                f = open('boss_says.txt', 'w')
                f.write(str(cmd))
                f.close()
                os.system("notepad.exe boss_says.txt")      
        except Exception as e:
            pass             

def send_intruder_detail():
    SUBJECT = "Someone trying to touch your computer"
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    body = "This is the person, and the sceenshot of that time: "+dt_string
    msg = MIMEMultipart()
    msg['From'] = BY
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body,'plane'))
    with open('intruder#'+str(count-2)+'.png', 'rb') as i:
        image_datai = i.read()
    with open('screen#'+str(count-2)+'.png', 'rb') as sc:
        image_datas = sc.read()    
    imageI = MIMEImage(image_datai, name=os.path.basename('intruder#'+str(count-1)+'.png'))
    imageS = MIMEImage(image_datas, name=os.path.basename('screen#'+str(count-1)+'.png'))
    msg.attach(imageI)
    msg.attach(imageS)
    s.send_message(msg)
    del msg
    
def get_command():
    status, messages = imap.select(mailbox='inbox', readonly=True)
    messages = int(messages[0])
    for i in range(messages, messages - 1, -1):
        # fetch the email message by ID
        res, msg = imap.fetch(message_set=str(i),message_parts="(RFC822)")  # msg gets tuple of message envelope and content
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])  # Message parser
                # decode the email subject
                subject = decode_header(msg["Subject"])[0][0] 
                if isinstance(subject, bytes):
                    subject = subject.decode()
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            return body
run()


