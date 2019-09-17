# -*- coding: utf-8 -*-
# Use Yagmail package to send email securely.
# pip install yagmail[all]
# pip install keyring[all]
# keyring set yagmail sender password
# keyring get yagmail sender
# keyring.set_password('yagmail', sender, password)
# keyring.get_password('yagmail', sender)
# yagmail.register(sender, password)
#
import yagmail

sender = 'foo.bar166@gmail.com'
receiver = 'foo.bar167@gmail.com'
subject = 'Yagmail test with attachment'
body = 'Hello there from Yagmail'
html = 'Hello from <a href="https://github.com/foobar167">FooBar167</a>!'
filenames = ['../data/doge.jpg', '../data/doge2.jpg', '../data/doge3.jpg']

yag = yagmail.SMTP(sender)
yag.send(
    to=receiver,
    subject=subject,
    contents=[body, html],
    attachments=filenames,
)
