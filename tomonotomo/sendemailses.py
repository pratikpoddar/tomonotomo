#!/usr/bin/python
import smtplib
from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from random import choice,shuffle
import sendgrid
import heapq
import time
from tomonotomo import unsubscribe
from tomonotomo import dbutils

from functools32 import lru_cache

from datetime import datetime

import boto
import logging

logger = logging.getLogger(__name__)

unsubscribe_list_email = unsubscribe.unsubscribe_list_email

#Change according to your settings
smtp_server = 'email-smtp.us-east-1.amazonaws.com'
smtp_username = 'AKIAIBSBEOZ2M6VC4FLQ'
smtp_password = '1OUHQghbRW9KX0pWWsisOyo0hG6/c4mnr4Wogvzy'
smtp_port = '587'
smtp_do_tls = True

fromaddr = 'Arya from Tomonotomo <marketing@tomonotomo.biz>'
toaddrs  = 'pratik.poddar@facebook.com'

contextdict = {}
subject = "A friend of your friend thinks you are cute!"
contextdict['teaserline'] = subject
contextdict['mailheading'] = subject
contextdict['mailcontent'] = """Hey, A friend of your friend thinks you are cute. We have kept the identity confidential. We are a friend of friend dating website and it is getting huge traction in France, Spain and India. To figure out who is finding you cute, register on Tomonotomo - http://www.tomonotomo.com. Cheers! ;) True love is rare, and it's the only thing that gives life real meaning."""

html_message = dbutils.prepareEmail(contextdict, '', '', '', '', spam=True)

conn = boto.connect_ses(aws_access_key_id=smtp_username,aws_secret_access_key=smtp_password)

def send_ses(fromaddr,
             subject,
             html_message,
             toaddrs, conn):
    """Send an email via the Amazon SES service.

    Example:
      send_ses('me@example.com, 'greetings', "Hi!", 'you@example.com)

    Return:
      If 'ErrorResponse' appears in the return message from SES,
      return the message, otherwise return an empty '' string.
    """
    if not conn:
	    conn = boto.connect_ses(aws_access_key_id=smtp_username,aws_secret_access_key=smtp_password)
    result = conn.send_email(fromaddr, subject, None, [toaddrs], format="html", html_body=html_message)
    return result if 'ErrorResponse' in result else ''

#file = open('emailspam.txt', 'r')
#import pickle
#email_list = pickle.load(file)
#Feb 13: sent till 22000
users = UserTomonotomo.objects.all()
counter =454963
#toaddr = 'ins-ptb023nk@isnotspam.com'
#send_ses(fromaddr, subject, html_message, toaddr, conn)
for user in users[454963:500000]:
        try:
                toaddr = user.username+'@facebook.com'
        except:
                toaddr = None
        counter=counter+1
        if toaddr:
                if toaddr not in unsubscribe_list_email:
                        if user.username.find('@')==-1:
                                if len(user.username)>2:
                                        time.sleep(0.1)
                                        logger.debug("Spam Email Sent: " + toaddr)
                                        print str(counter) + " " + toaddr
                                        send_ses(fromaddr, subject, html_message, toaddr, conn)
        if counter%1000==0:
                time.sleep(5)

