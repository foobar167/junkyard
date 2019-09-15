# -*- coding: utf-8 -*-
# Create an unsecured SMTP connection and encrypt it using .starttls()
import ssl
import smtplib
import getpass

smtp_server = 'smtp.gmail.com'
port = 587  # starttls port
sender_email = 'foo.bar166@gmail.com'
receiver_email = 'foo.bar167@gmail.com'

message = """\
Subject: Hi there

This message is sent from Python.
"""

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
server = None
try:
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()  # can be omitted
    server.starttls(context=context)  # encrypt the connection
    server.ehlo()  # can be omitted
    password = getpass.getpass(prompt='Enter password for {}: '.format(sender_email), stream=None)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
except smtplib.SMTPAuthenticationError as err:
    print(err.smtp_error.decode())
finally:
    if server is not None:
        server.quit()
