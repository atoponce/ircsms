#!/usr/bin/python

import base64
import email.utils
import re
import smtplib
import time
import yaml
import zmq
from email.mime.text import MIMEText

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, '')
socket.connect('tcp://127.0.0.1:2428')

while True:
    f = open('/var/log/0mq.log','a')
    msg = socket.recv()
    msg = re.sub('\n:', '\n', msg)
    msg = re.sub('^---| !binary \|-\n','',msg)
    y = yaml.load(msg)

    f.write(msg)
    f.close()

    nick = base64.b64decode(y.items()[0][1][3])
    server = base64.b64decode(y.items()[2][1])
    epoch = base64.b64decode(y.items()[3][1])
    message = base64.b64decode(y.items()[5][1])
    channel = base64.b64decode(y.items()[7][1])

    nick = re.sub('^nick_','',nick)
    if nick == 'prefix_nick_white':
        nick = 'eightyeight'

    mt = time.localtime(int(epoch))
    d = time.strftime('%H:%M:%S', mt)

    fromaddr = 'weechat@irc.ae7.st'
    toaddr = '8019206031@messaging.sprintpcs.com'
    msg = MIMEText("{0}/{1}: <{2}> {3}".format(d, server, channel, nick, message))
    msg['To'] = email.utils.formataddr(('eightyeight', toaddr))
    msg['From'] = email.utils.formataddr(('WeeChat', fromaddr))

    s = smtplib.SMTP('localhost')
    s.sendmail(fromaddr, [toaddr], msg.as_string())
    s.quit()
