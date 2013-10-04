import logging
from social_auth.exceptions import AuthCanceled
from django.shortcuts import render, redirect


logger = logging.getLogger(__name__)

class error500Middleware(object):
        def process_exception(self, request, exception):
		if isinstance(exception, AuthCanceled): 
			return redirect('/home')
		else:		
	                logger.exception('tomonotomo_project.middleware.error500Middleware')
	                return None

