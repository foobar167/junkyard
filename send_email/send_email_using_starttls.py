# -*- coding: utf-8 -*-
# Create an unsecured SMTP connection and encrypt it using .starttls()
import os
import ssl
import smtplib
import getpass

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = 'smtp.gmail.com'
port = 587  # starttls port
sender_email = 'foo.bar166@gmail.com'
receiver_email = 'foo.bar167@gmail.com'
password = getpass.getpass(prompt='Enter password for {}: '.format(sender_email), stream=None)

# Create the plain-text and HTML version of your message
subject = 'Multipart test email with attachment - 2'

text = """\
Hi, :-)
How are you?
Real Python has many great tutorials:
www.realpython.com"""

html = """\
<html>
  <body>
    <p>Hi,<br>
       How are you?<br>
       <a href="http://www.realpython.com">Real Python</a> 
       has many great tutorials.
    </p>
  </body>
</html>
"""

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message = MIMEMultipart('alternative')
message['Subject'] = subject
message['From'] = sender_email
message['To'] = receiver_email
message["Bcc"] = receiver_email  # recommended for mass emails
message.attach(MIMEText(text, 'plain'))
message.attach(MIMEText(html, 'html'))

filepath = '../various/doge2.jpg'
filename = os.path.basename(filepath)

# Open file in binary mode
with open(filepath, 'rb') as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header('Content-Disposition', f'attachment; filename= {filename}',)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
server = None
try:
    server = smtplib.SMTP(smtp_server, port)
    server.starttls(context=context)  # encrypt the connection
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)
except smtplib.SMTPAuthenticationError as err:
    print(err.smtp_error.decode())
finally:
    if server is not None:
        server.quit()
