import os
import smtplib, ssl
import docx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template
from pathlib import Path
from openpyxl import load_workbook


def send_email(from_email, to_email, subject, text, server):
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    # part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    # message.attach(part2)

    # Create secure connection with server and send email
    server.sendmail(from_email, to_email, message.as_string())


def send_from_template(template, to_email, **data):
    context = ssl.create_default_context()

    url = "smtp.gmail.com"
    port = 465
    username = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")

    with open(f"/src/templates/{template}.txt", "r") as f:
        text_template = Template(f.read())

    with smtplib.SMTP_SSL(url, port, context=context) as server:
        server.login(username, password)
        text = text_template.substitute(**data)
        sender_email = username
        subject = text.partition('\n')[0]
        send_email(sender_email, to_email, subject, text, server)

def clean_temp_after_run(func):
    def wrapper(*args, **kwargs):
        val = func(*args, **kwargs)
        for temp_file in Path().glob('_temp.*'):
            os.remove(temp_file)
        return val
    return wrapper

def create_temp(fd, ext):
    temp = open('_tmp.'+ ext, 'wb')
    fd = fd.read()
    temp.write(fd)
    return temp

@clean_temp_after_run
def check_file(file, document: str) -> bool:
    if not file:
        return False
    d = ''.join(document.split('-'))
    secure_key = d[:len(d)-5].lower()
    ext = file.name[-4:]
    if ext == 'docx':
        doc = docx.Document(file)
        if doc.core_properties.keywords == secure_key:
            return True
    elif ext == 'xlsx':
        wb = load_workbook(file)
        if wb.properties.keywords == secure_key:
            return True
    return False