import logging
from social_auth.exceptions import AuthCanceled, SocialAuthBaseException
from django.shortcuts import render, redirect


logger = logging.getLogger(__name__)

class error500Middleware(object):
        def process_exception(self, request, exception):
		if isinstance(exception, AuthCanceled): 
			return redirect('/home')
		if isinstance(exception, SocialAuthBaseException):
			return redirect('/loginerror')
		else:		
	                logger.exception('tomonotomo_project.middleware.error500Middleware')
	                return None

