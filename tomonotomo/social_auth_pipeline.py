from django.utils import simplejson
from django.http import Http404, HttpResponse, HttpResponseRedirect
from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
from django.contrib.auth import get_user_model

from tomonotomo.models import UserTomonotomo, UserFriends

from django.db import transaction

@transaction.commit_manually
def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        print "Creating Custom User"

        if kwargs['is_new'] == False:
            print "Returning user " +  str(user)
            transaction.commit()
            return

        print "Getting data for first time user " +  str(user)

        if user is None:
                print "User came as None in the function create_custom_user"
                transaction.commit()
                return
        if backend.__class__ != FacebookBackend:
                transaction.commit()
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
        profile.gender = res.get('gender') or "not specified"

        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name')
        if res.get('location'):
                profile.location = res.get('location').get('name')
        profile.username = res.get('username')
        profile.userid = res.get('id')

        print "Getting data for userid " + profile.userid

        print "----"

        graph = GraphAPI(res.get('access_token'))

        responsegraph = graph.get(str(res['id'])+'?fields=birthday')
        profile.birthday = str(responsegraph.get('birthday'))

        responsegraph = graph.get(str(res['id'])+'/friends?fields=id,name,gender')
        profile.friends = str(responsegraph.get('data'))

        print "----"

        profile.save()

        transaction.commit()

        print "----"

        userloggedin = UserTomonotomo.objects.get(userid=res['id'])

        for friend in responsegraph.get('data'):
                print "|||"
                print "Saving information for friendid - " + friend.get('id')
                profilefriends = UserFriends(userid = userloggedin,
                        friendid = friend.get('id'), 
                        friendname = friend.get('name'),
                        friendgender = friend.get('gender') or "not specified")

                profilefriends.save()

        print "----"

        transaction.commit()
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