#!/usr/bin/python

# Copyright (c) 2013 by Aaron Toponce <aaron.toponce@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64
import email.utils
import re
import smtplib
import yaml
import zmq
from email.mime.text import MIMEText
from urllib import urlencode
from urllib2 import urlopen

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

    # Regex from John Anderson <sontex@gmail.com> in:
    # http://weechat.org/scripts/source/shortenurl.py.html/
    octet = r'(?:2(?:[0-4]\d|5[0-5])|1\d\d|\d{1,2})'
    ipAddr = r'%s(?:\.%s){3}' % (octet, octet)
    # Base domain regex off RFC 1034 and 1738
    label = r'[0-9a-z][-0-9a-z]*[0-9a-z]?'
    domain = r'%s(?:\.%s)*\.[a-z][-0-9a-z]*[a-z]?' % (label, label)
    urlRe = re.compile(r'(\w+://(?:%s|%s)(?::\d+)?(?:/[^\])>\s]*)?)' % (domain, ipAddr), re.I)
    
    # Shorten URLs
    for url in urlRe.findall(message):
        if len(url) > 26: # should handle most urls already shortened
            try:
                # Change your 'shrinkme' url as needed. Adjust FIXME and
                # urlencode() as necessary.
                shrinkme = 'http://example.com/yourls-api.php?signature=FIXME&action=shorturl&format=simple&{0}'.format(urlencode({'url': url}))
                shorturl = urlopen(shrinkme).read()
                message = message.replace(url, shorturl)
            except:
                continue

    # Change your email-to-sms address as provided by your mobile provider
    fromaddr = 'weechat@irc.example.com'
    toaddr = '1234567890@messaging.sprintpcs.com'
    msg = MIMEText("{0}/{1}: {2}".format(channel, nick, message))
    msg['To'] = email.utils.formataddr(('eightyeight', toaddr))
    msg['From'] = email.utils.formataddr(('WeeChat', fromaddr))

    s = smtplib.SMTP('localhost')
    s.sendmail(fromaddr, [toaddr], msg.as_string())
    s.quit()
