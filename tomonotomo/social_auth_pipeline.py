from django.utils import simplejson
from django.http import Http404, HttpResponse, HttpResponseRedirect
from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
from django.contrib.auth import get_user_model

import pprint


def populate_user_info(backend, details, response, social_user, uid, user, *args, **kwargs):

        pprint("ddfdf")

        if user is None:
                return
        if backend.__class__ != FacebookBackend:
                return

        profile = user.get_profile()
        profile.uid = response['id']
        access_token = UserSocialAuth.objects.filter(provider='facebook').get(uid=response['id']).tokens['access_token']
        graph = GraphAPI(access_token)
        res = graph.get(str(uid)+'?fields='+reduce(lambda x,y: x+','+y,DATA_FIELDS))
        profile.accesstoken = access_token
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.birthday = res.get('birthday')
        profile.fullname = res.get('name')
        profile.gender = res.get('gender')
        if res.get('location'):
                profile.location = res.get('location').get('name','')
        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name','')
        if res.get('work'):
                profile.work= getSanitizedWork(res['work'])
        if res.get('education'):
                profile.education= getSanitizedWork(res['education'])

        utnt = UserTomonotomo(profile)
        utnt.save()
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