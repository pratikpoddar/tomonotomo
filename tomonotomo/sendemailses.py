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

fromaddr = 'Sheetal from Tomonotomo <marketing@tomonotomo.biz>'
#toaddrs  = 'pratikpoddar05051989@gmail.com'

contextdict = {}
subject = "Single this Valentine? Please give us a shot! - Tomonotomo"
contextdict['teaserline'] = subject
contextdict['mailheading'] = subject
contextdict['mailcontent'] = """Hey, This is Sheetal from New Delhi. We just launched a friend of friend dating website and it is getting huge traction in France, Spain and India. Requesting you to please give it a shot. Please visit http://www.tomonotomo.com (Tomonotomo) and let us know your thoughts. We blog at http://tomonotomo.wordpress.com . We believe that we are revolutionising the way dating happens. 

Tomonotomo is short for 'tomodachi no tomodachi' which is japanese for 'Friends of Friends'. You see only profiles of friends of friends and only friends of friends see your profile. Its a gender balanced dating network (40-60 distribution). You contact the people you like in three ways: Ask friend to introduce, Contact friend of friend directly, and Just mention that you secretly admire a friend of friend. If he/she also feels the same way, we will connect you two after taking permission from you. Since, explicity or implicitly, there is always a common friend involved, the system ensures more safety, trust and friendliness. 

Its free only till Feb 14th. Hop on the bangwagon while its free. Do it now! Login at http://www.tomonotomo.com"""

html_message = dbutils.prepareEmail(contextdict, '', '', '', '', spam=True)

def send_ses(fromaddr,
             subject,
             html_message,
             toaddrs):
    """Send an email via the Amazon SES service.

    Example:
      send_ses('me@example.com, 'greetings', "Hi!", 'you@example.com)

    Return:
      If 'ErrorResponse' appears in the return message from SES,
      return the message, otherwise return an empty '' string.
    """
    conn = boto.connect_ses(aws_access_key_id=smtp_username,aws_secret_access_key=smtp_password)
    result = conn.send_email(fromaddr, subject, None, [toaddrs], format="html", html_body=html_message)
    return result if 'ErrorResponse' in result else ''

file = open('emailspam.txt', 'r')
import pickle
email_list = pickle.load(file)

for toaddr in email_list[7000:11000]:
	if toaddr not in unsubscribe_list_email:
		time.sleep(0.3)
		logger.debug("Spam Email Sent: " + toaddr)
		send_ses(fromaddr, subject, html_message, toaddr)

