from django.utils import simplejson
from django.http import Http404, HttpResponse, HttpResponseRedirect
from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
from django.contrib.auth import get_user_model

from tomonotomo.models import UserTomonotomo, UserFriends


def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        ## TODO: Sometimes user comes as none. Why?
        if user is None:
                return
        if backend.__class__ != FacebookBackend:
                return

        res = kwargs['response']

        profile = UserTomonotomo() 
        profile.accesstoken = res.get('access_token')
        profile.expiresin = res.get('expires')
        if res.get('work'):
                profile.work= getSanitizedWork(res['work'])
        if res.get('education'):
                profile.education= getSanitizedEducation(res['education'])
        profile.email = res.get('email')
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.gender = res.get('gender')
        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name')
        if res.get('location'):
                profile.location = res.get('location').get('name')
        profile.username = res.get('username')
        profile.userid = res.get('id')

        print "Getting data for userid " + profile.userid

        print "----"

        graph = GraphAPI(res.get('access_token'))

        responsegraph = graph.get(str(res['id'])+'?fields=friends, birthday')
        profile.friends = responsegraph.get('friends').get('data')
        profile.birthday = str(responsegraph.get('birthday'))

        print "----"

        profile.save()

        print "----"

        ## TODO: Make it faster - Optimize it
        ## TODO: Prevent Database locking

        for friend in profile.friends:
                print "Saving information for friendid - " + friend.get('id')
                profilefriends = UserFriends(userid = res['id'], 
                        friendid = friend.get('id'), 
                        friendname = friend.get('name'))
                profilefriends.save()

        return

def getSanitizedEducation (educationProfile):
        """ Helper function to get education profile as a structured string """
        education = ""
        for value in educationProfile:
                if value.get('school') and value['school'].get('name'):
                        education = education + value['school']['name']+'---'
                if value.get('concentration'):
                        for concentration in value['concentration']:
                                education = education + concentration['name']+'---'
        return education

def getSanitizedWork (workProfile):
        """ Helper function to get work profile as a structured string """
        work = ""
        for value in workProfile:
                if value.get('employer') and value['employer'].get('name'):
                        work = work + value['employer']['name']+'---'
        return work