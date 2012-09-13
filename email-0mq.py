#!/usr/bin/python

import base64
import email.utils
import re
import smtplib
import yaml
import zmq
from email.mime.text import MIMEText

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')
socket.connect('tcp://127.0.0.1:2428')

while True:
    msg = socket.recv()
    msg = re.sub('\n:', '\n', msg)
    msg = re.sub('^---| !binary \|-\n','',msg)
    y = yaml.load(msg)

    f = open('/var/log/0mq.log','a')
    f.write(msg)
    f.close()

    try:
        nick = base64.b64decode(y['tags'][3])
        nick = re.sub('^nick_','',nick)
    except:
        continue

    message = base64.b64decode(y['message'])
    channel = base64.b64decode(y['channel'])

    # Change your email-to-sms address as provided by your mobile provider
    fromaddr = 'weechat@irc.example.com'
    toaddr = '1234567890@messaging.sprintpcs.com'
    msg = MIMEText("{0}/{1}: {2}".format(channel, nick, message))
    msg['To'] = email.utils.formataddr(('eightyeight', toaddr))
    msg['From'] = email.utils.formataddr(('WeeChat', fromaddr))

    s = smtplib.SMTP('localhost')
    s.sendmail(fromaddr, [toaddr], msg.as_string())
    s.quit()
