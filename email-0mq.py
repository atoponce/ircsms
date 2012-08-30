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
    f = open('/var/log/0mq.log','a')
    msg = socket.recv()
    msg = re.sub('\n:', '\n', msg)
    msg = re.sub('^---| !binary \|-\n','',msg)
    y = yaml.load(msg)

    f.write(msg)
    f.close()

    # When day changes, the 'tags' value list will be empty. Ignore.
    if y.values()[0] == []:
        pass

    # Format is:
    # ['tags', 'away', 'server', 'date', 'highlight', 'message', 'type', 'channel']
    # where 'tags' is another list of items.
    server = base64.b64decode(y.values()[2])
    channel = base64.b64decode(y.values()[7])
    nick = base64.b64decode(y.values()[0][3])
    nick = re.sub('^nick_','',nick)
    message = base64.b64decode(y.values()[5])

    # If sending messages to the channel while away, it shows up as
    # "prefix_nick_white". This can change it to your nick.
    if nick == 'prefix_nick_white':
        nick = 'eightyeight'

    # Change your email-to-sms address as provided by your mobile provider
    fromaddr = 'weechat@irc.example.com'
    toaddr = '1234567890@messaging.sprintpcs.com'
    msg = MIMEText("{0}/{1}: <{2}> {3}".format(server, channel, nick, message))
    msg['To'] = email.utils.formataddr(('eightyeight', toaddr))
    msg['From'] = email.utils.formataddr(('WeeChat', fromaddr))

    s = smtplib.SMTP('localhost')
    s.sendmail(fromaddr, [toaddr], msg.as_string())
    s.quit()
