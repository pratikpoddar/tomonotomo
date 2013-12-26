from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
import time
import pprint
from random import randint, shuffle
from datetime import datetime
from datetime import timedelta
import simplejson
import urllib2
import pickle
from tomonotomo.models import UserTomonotomo, UserFriends, UserProcessing, UserLogin, UserQuota, UserLocation
from profiling import profile

import pytz

import dbutils
from django.db import transaction

from django_cron import CronJobBase, Schedule

import logging

logger = logging.getLogger(__name__)

genderdict = { "male":1, "female":2, "not specified":3 }
relstatusdict = { "Single":1, "Engaged":2, "Married":2, "In a relationship":2, "It's complicated":3, "In an open relationship":3, "Widowed":3, "Separated":3, "Divorced":3, "In a civil union":3, "In a domestic partnership":3, "not specified":3 }

@profile 
def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        logger.debug("social_auth_pipeline.create_custom_user - Creating Custom User")

        ## TODO: Make not updating condition stricter. stop only if (not new) and (updated in last 10 days)
        if kwargs['is_new'] == False:
        	logger.debug("social_auth_pipeline.create_custom_user - Returning user " + str(user))
	else:
        	logger.debug("social_auth_pipeline.create_custom_user - Getting data for first time user " + str(user))

        if user is None:
                logger.exception("social_auth_pipeline.create_custom_user - User came as None in the function create_custom_user")
                return
        if backend.__class__ != FacebookBackend:
                return

        res = kwargs['response']

	logger.debug("social_auth_pipeline.create_custom_user - Getting/Updating data for userid " + res.get('id'))
	logger.debug("social_auth_pipeline.create_custom_user - " + str(res))

        try:
            profile = UserTomonotomo.objects.get(userid=res.get('id'))
        except UserTomonotomo.DoesNotExist:
            profile = UserTomonotomo()

        profile.accesstoken = res.get('access_token')
        profile.expiresin = res.get('expires')
        if res.get('work'):
                profile.work= getSanitizedWork(res['work'])
        if res.get('education'):
                profile.education= getSanitizedEducation(res['education'])
        profile.email = res.get('email')
	if not res.get('email'):
		profile.email = str(res.get('username'))+"@facebook.com"
		logger.info("social_auth_pipeline.create_custom_user - Email not found for user " + str(res.get('id')) + ". Using " + profile.email)
		if not res.get('username'):
			logger.exception("social_auth_pipeline.create_custom_user - Critical - Could neither get email nor username@facebook.com for user " + str(res.get('id')))
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.gender = genderdict[res.get('gender') or "not specified"]
        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name')
        if res.get('location'):
                profile.location = res.get('location').get('name')
		saveLocation(res.get('location').get('id'))
	if res.get('relationship_status'):
		profile.relstatus = relstatusdict[res.get('relationship_status') or "not specified"]
        profile.username = res.get('username')
        profile.userid = res.get('id')

        # "----"

        graph = GraphAPI(res.get('access_token'))
        responsegraph = graph.get(str(res['id'])+'?fields=birthday,likes')
        profile.birthday = str(responsegraph.get('birthday'))
	try:
		if responsegraph.get('likes'):
			# TODO: Gets interests only if interests are not there. Need to change this.
			if not profile.interests:
				profile.interests = pickle.dumps(extractAllSanitizedLikes(responsegraph.get('likes'))).decode('latin1')
	except Exception as e:
		logger.exception("social_auth_pipeline.create_custom_user - Error getting likes for user " + str(res.get('id')))

        profile.save()

        # "----"

        userloggedin = UserTomonotomo.objects.get(userid=res['id'])

	# "----"

        try:
            userprocessing = UserProcessing.objects.get(userloggedin=userloggedin)
        except UserProcessing.DoesNotExist:
            userprocessing = UserProcessing()
            userprocessing.userloggedin = userloggedin
        except UserProcessing.MultipleObjectsReturned:
            userprocessing = userProcessing()
            userprocessing.userloggedin = userloggedin

        userprocessing.accesstoken = res.get('access_token')

        userprocessing.save()

	# "----"

	try:
		userquota = UserQuota.objects.get(userid=res.get('id'))
	except UserQuota.DoesNotExist:
		userquota = UserQuota()
		userquota.userid = res.get('id')
		userquota.quota=20
		userquota.save()

	# "----"

	if kwargs['is_new']==False:
		logger.debug("social_auth_pipeline.create_custom_user - completed for returning user " + str(res.get('id')))
		return

        friendlist = graph.fql('SELECT uid2 FROM friend where uid1=me()')
        peopleontnt = UserTomonotomo.objects.values('userid')

        friendsontnt = list(set(map(lambda x: int(x['uid2']), friendlist.get('data'))) & set(map(lambda x: x['userid'], peopleontnt)))
	
        for friendontnt in friendsontnt:
            try:
                profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=friendontnt)
            except UserFriends.DoesNotExist:
                profilefriends = UserFriends()
                profilefriends.userid = userloggedin
                profilefriends.friendid = friendontnt
		try:
	                profilefriends.save()
		except:
			pass

	friendsregisteredontnt = list(set(friendsontnt) & set(map(lambda x: x['userid'], UserTomonotomo.objects.exclude(email=None).values('userid'))))
	shuffle(friendsregisteredontnt)
	for friendontnt in friendsregisteredontnt[:10]:
	    try:
		dbutils.sendemailnotification(friendontnt, "One of your friends just joined tomonotomo", "One of your friends just joined tomonotomo to meet interesting friends of friends. We'll keep the name of your friend to ourselves out of respect for his privacy. A new friend is a good news for you as your friend of friend network just increased by "+ str(400 + randint(0,200)) + ", and you have a larger pool of potential dates. Congratulations and visit www.tomonotomo.com right away!")
	    except Exception as e:
		logger.exception("social_auth_pipeline.create_custom_user - error in sendemailnotification " + str(e) + str(friendontnt))
		pass
	
        # "----"

        logger.debug("social_auth_pipeline.create_custom_user - completed for first time user " + str(userloggedin))
        return

def getSanitizedEducation (educationProfile):
        """ Helper function to get education profile as a structured string """
        education = ""
        for value in educationProfile:
                if value.get('school') and value['school'].get('name'):
                        education = education + value['school']['name']+'---'
        return education

def getSanitizedWork (workProfile):
        """ Helper function to get work profile as a structured string """
        work = ""
        for value in workProfile:
                if value.get('employer') and value['employer'].get('name'):
                        work = work + value['employer']['name']+'---'
        return work

def extractAllSanitizedLikes (likeResFBGraph):
	
	likesResult = []
	likesResult.extend(getSanitizedLikes(likeResFBGraph['data']))
	try:
		likesResult.extend(getAllLikes(likeResFBGraph['paging']['next']))
	except:
		pass
	return likesResult

def getAllLikes (likelink):
	
	likesdata = simplejson.load(urllib2.urlopen(likelink))
	likesList = []
	likesList.extend(getSanitizedLikes(likesdata['data']))
	try:
		likesList.extend(getAllLikes(likesdata['paging']['next']))
	except:
		pass
	return likesList

def getSanitizedLikes (likesList):
        """ Helper function to get likes as a structured string """
	likesResult = []
	for likevalue in likesList:
		try:
			likesResult.append({'page_id': int(likevalue['id']), 'name': likevalue['name']})
		except:
			pass
	return likesResult

def saveLocation (locationid):

	try:
		if UserLocation.objects.filter(locationid=locationid).count()==0:
			logger.debug("saveLocation - saving Location info for " + str(locationid))
			locationjson = simplejson.load(urllib2.urlopen('https://graph.facebook.com/'+str(locationid)))
			loc = UserLocation()
			loc.locationid = locationid
			loc.userlocation = locationjson['name']
			if locationjson.get('location'):
				loc.latitude = locationjson['location']['latitude']
				loc.longitude = locationjson['location']['longitude']
				if loc.latitude and loc.longitude:
					loc.save()
	except Exception as e:
		logger.exception('saveLocation - error - locationid - ' + str(locationid) + ' - ' + str(e))
		pass

	return

def postProcessing(userid, accessToken):

	userloggedin = UserTomonotomo.objects.get(userid=userid)
        graph = GraphAPI(accessToken)
        logger.debug("social_auth_pipeline.postProcessing - Processing " + accessToken + " - " + str(userid))
	try:
		## Checking if accesstoken is valid
        	friendnumber = graph.fql('SELECT friend_count FROM user where uid=me()')
        	numberfriends = friendnumber.get('data')[0].get('friend_count')
        	logger.debug("social_auth_pipeline.postProcessing - number of friends " + str(numberfriends))
	except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Accesstoken is invalid - " + str(e) + " - " + str(e.args))
		raise

        friendgraphdata= []
        friendgraph= []
        for i in range(0,10):
            query = 'SELECT uid,first_name,last_name,username,name,birthday,education,work,sex,hometown_location,current_location,relationship_status FROM user WHERE uid in (SELECT uid2 FROM friend where uid1=me() limit '+str(max(0,(i*500)-100))+',500)'
            friendgraphdata.append(graph.fql(query))
            friendgraph.extend(friendgraphdata[i].get('data'))
            logger.debug("social_auth_pipeline.postProcessing - received data for " + str(len(friendgraph)) + " friends - some are duplicate")

        logger.debug("social_auth_pipeline.postProcessing - list of friends data "+str(len(friendgraph))+" - some are duplicate")

        count = 0
	fqlerror = 0
        for frienddata in friendgraph:

            count = count + 1
	    try:
	            logger.debug("social_auth_pipeline.postProcessing - Saving detailed information for friendid - " + str(frienddata.get('uid')) + " - count " + str(count))
	    except:
		    logger.exception("social_auth_pipeline.postProcessing - Saving detailed information for friendid without uid - " + str(frienddata) + " - count " + str(count))

            try:
		profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=frienddata.get('uid'))
            except UserFriends.DoesNotExist:
                profilefriends = UserFriends()
                profilefriends.userid = userloggedin
                profilefriends.friendid = frienddata.get('uid')
		try:
                	profilefriends.save()
		except Exception as e:
			logger.exception("social_auth_pipeline.postProcessing - Exception saving userfriends data - error - " + str(frienddata.get('uid')) + " - " + str(e.args))
			pass
	    except UserFriends.MultipleObjectsReturned:
		logger.exception("social_auth_pipeline.postProcessing - Exception saving userfriends data - multiple entries in userfriends race error " + str(frienddata.get('uid')))
            	pass
	    except Exception as e:
		try:
			logger.exception("social_auth_pipeline.postProcessing - Exception saving UserFriends - " + str(frienddata) + " " + str(e.args))
		except:
			pass

		logger.exception("social_auth_pipeline.postProcessing - Exception saving UserFriends - " + str(e) + " - " + str(e.args))
		raise

	    try:
                userfriend = UserTomonotomo.objects.get(userid=frienddata.get('uid'))
            except UserTomonotomo.DoesNotExist:
                userfriend = UserTomonotomo()

	    try:	     
            	if frienddata.get('work'):
               		userfriend.work= getSanitizedWork(frienddata['work'])
            	if frienddata.get('education'):
                	userfriend.education= getSanitizedEducation(frienddata['education'])
            	userfriend.first_name = frienddata.get('first_name')
           	userfriend.last_name = frienddata.get('last_name')
		try:
            		userfriend.gender = genderdict[frienddata.get('sex') or "not specified"]
		except:
			userfriend.gender = genderdict["not specified"]
           	if frienddata.get('hometown_location'):
                	userfriend.hometown = frienddata.get('hometown_location').get('name')
            	if frienddata.get('current_location'):
                	userfriend.location = frienddata.get('current_location').get('name')
			saveLocation(frienddata.get('current_location').get('id'))

		try:
			userfriend.relstatus = relstatusdict[frienddata.get('relationship_status') or "not specified"]
		except:
			userfriend.relstatus = relstatusdict["not specified"]

            	userfriend.username = frienddata.get('username')
            	userfriend.userid = frienddata.get('uid')
            
	    	if frienddata.get('birthday'):
                	try:
                    		userfriend.birthday = time.strftime("%m/%d/%Y", time.strptime(frienddata.get('birthday'), "%B %d, %Y"))
                	except:
                    		pass

		try:
			# TODO: Gets interests only if interests are not there. Need to change this.
			if (not userfriend.interests) and (not fqlerror):
				query = 'SELECT page_id, name FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=' + str(frienddata.get('uid')) + ')'
				userfriend.interests = pickle.dumps(graph.fql(query).get('data')).decode('latin1')
		except Exception as e:
			fqlerror = 1
			logger.exception("social_auth_pipeline.postProcessing - Error getting friends' likes - " + str(frienddata.get('uid')) + " - " + str(e.args))
			pass

	    except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Error collecting information - " + str(e) + " - " + str(e.args))
		raise

	    try:
            	userfriend.save()
	    except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Error saving userdata - " + str(e) + " - " + str(e.args))
		raise

        return

class startPostProcessing(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'tomonotomo.social_auth_pipeline.startPostProcessing'    # a unique code

    def do(self):
	logger.debug("social_auth_pipeline.startPostProcessing - StartPostProcessing starts")
        pendingusers = UserProcessing.objects.filter(entryaddtime__lte=datetime.now(pytz.timezone('America/Chicago'))+timedelta(minutes=-10)).values('userloggedin','accesstoken')
	logger.debug("social_auth_pipeline.startPostProcessing - StartPostProcessing starts - length of list is " + str(len(pendingusers)))
        if len(pendingusers) > 0:
        	randnum = randint(0, len(pendingusers)-1)
		userloggedin = pendingusers[randnum].get('userloggedin')
                accesstoken = pendingusers[randnum].get('accesstoken')
		
		UserProcessing.objects.filter(userloggedin = userloggedin).delete()
            	userprocessing = UserProcessing()
	        userprocessing.userloggedin = UserTomonotomo.objects.get(userid=userloggedin)
		userprocessing.accesstoken = accesstoken
		userprocessing.save()

                try:
			logger.debug("social_auth_pipeline.startPostProcessing - Starting Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
                	postProcessing(userloggedin, accesstoken)
			logger.debug("social_auth_pipeline.startPostProcessing - Almost Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
                	UserProcessing.objects.filter(userloggedin = userloggedin).delete()
                	logger.debug("social_auth_pipeline.startPostProcessing - Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
        	except:
            		logger.exception("social_auth_pipeline.startPostProcessing - Failed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)

		logger.debug("social_auth_pipeline.startPostProcessing - Before this operation - length of list was " + str(len(pendingusers)))

    	return

class updateQuota(CronJobBase):
	RUN_AT_TIMES = ['00:00']
	schedule = Schedule(run_at_times=RUN_AT_TIMES)
	code='tomonotomo.social_auth_pipeline.updateQuota'

	def do(self):
		logger.debug("social_auth_pipeline.updateQuota - UpdateQuota starts")
		users = UserTomonotomo.objects.all().exclude(email=None).values('userid')
		for user in users:
			try:
                		userquota = UserQuota.objects.get(userid=user['userid'])
				userquota.quota=20
        		except UserQuota.DoesNotExist:
                		userquota = UserQuota(userid=user['userid'], quota=30)
                	userquota.save()

		logger.debug("social_auth_pipeline.updateQuota - Done UpdateQuota")
		return

