from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from tomonotomo.models import UserTomonotomo

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend

# from profile.models import Profile

def index(request):
    return render(request, 'tomonotomo/index.html')

def friend(request):
	template = loader.get_template('tomonotomo/friend.html')
	context = RequestContext(request, {
		'fbid': 717323242,
		'fullname': "Pratik Poddar",
		'age': '24',
		'location': 'Mumbai, India',
		'worklist': ['Clipr', 'Blackstone', 'Morgan Stanley'],
		'educationlist': ['Stanford', 'IIT Bombay'],
		'mutualfriends': ['Sachin Tendulkar', 'Aniket Behera', 'Huma Kureshi'],
		})
	return HttpResponse(template.render(context))

def about(request):
    return render(request, 'tomonotomo/about.html')

def join(request):
    return render(request, 'tomonotomo/join.html')


