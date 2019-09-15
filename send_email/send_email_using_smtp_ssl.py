# -*- coding: utf-8 -*-
# Use .SMTP_SSL() to create a connection that is secure from the outset
import ssl
import smtplib
import getpass

port = 465  # SSL port
sender_email = 'foo.bar166@gmail.com'
receiver_email = 'foo.bar167@gmail.com'

message = """\
Subject: Hi there

This message is sent from Python.
"""

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
    try:
        password = getpass.getpass(prompt='Enter password for {}: '.format(sender_email), stream=None)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    except smtplib.SMTPAuthenticationError as err:
        print(err.smtp_error.decode())
