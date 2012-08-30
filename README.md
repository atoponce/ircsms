# IRC-to-SMS

This script provides a 0mq client to subscribe to IRC events, and send them
to a moble number using an email-to-sms gateway provided by a mobile
provider. See https://en.wikipedia.org/wiki/List\_of\_SMS\_gateways for a list
of providers.

## Requirements

This script relies on a 0mq Ruby script for WeeChat which can be found
here: http://weechat.org/scripts/source/stable/zmq\_notify.rb.html/. The
Ruby script creates a YAML load (not valid, but meh) and sets up a PUB 0mq
socket to send the message to. So, some requirements must be met for that
to work:

- weechat-curses (compiled with Ruby support)
- ruby1.9.1
- ruby1.9.1-dev
- 0mq (can be installed with "gem install zmq")

Restart WeeChat, load the script, and bind the socket to localhost on port
2428:

    /ruby load zmq\_notify.rb
    /set plugins.var.ruby.zmq_notify.endpoint tcp://127.0.0.1:2428

You should notice a TCP socket created, and listening for connections. This
is your 0mq socket. Now, you need to setup the requirements necessary for
this Python script:

- python2.7
- python-zmq
- python-yaml
- A running SMTP server that can send outbound email

## Installation

I setup the script to execute in /etc/rc.local using the following code:

    $ cat /etc/rc.local
    /usr/local/bin/email-0mq.py 2> /var/log/0mq.err > /dev/null &

Then I can '/etc/init.d/rc.local stop' and '/etc/init.d/rc.local start' as
needed. A proper init script should probably be written, and I'll
eventually provide one here.

At this point, you should be able to enable the script to bind the socket
from your WeeChat client

    /set plugins.var.ruby.zmq_notify.enabled on

Now start the Python script from the shell:

    # /etc/init.d/rc.local start

And verify that it has established the connection:

    $ netstat -taupen | grep 2428
    tcp  0 0 127.0.0.1:2428   0.0.0.0:*        LISTEN      1000   7333346  3205/weechat-curses
    tcp  0 0 127.0.0.1:33115  127.0.0.1:2428   ESTABLISHED 0      7335329  26786/python    
    tcp  0 0 127.0.0.1:2428   127.0.0.1:33115  ESTABLISHED 1000   7335330  3205/weechat-curses

Because there is logging to /var/log/, you may want to configure logrotate
to rotate the log files. Here is what I added to my configs:

    $ cat /etc/logrotate.d/0mq
    /var/log/0mq.err {
      rotate 6
      daily
      compress
      missingok
      notifempty
    }
    /var/log/0mq.out {
      rotate 6
      daily
      compress
      missingok
      notifempty
    }
