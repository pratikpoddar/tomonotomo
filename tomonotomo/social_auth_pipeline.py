from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
import time
import pprint
from random import randint

from tomonotomo.models import UserTomonotomo, UserFriends, UserProcessing, UserLogin, UserQuota

from django.db import transaction

from django_cron import CronJobBase, Schedule

genderdict = { "male":1, "female":2, "not specified":3 }

def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        print "Creating Custom User"

        ## TODO: Make not updating condition stricter. stop only if (not new) and (updated in last 10 days)
        if kwargs['is_new'] == False:
        	print "Returning user " + str(user)
	else:
        	print "Getting data for first time user " + str(user)

        if user is None:
                print "User came as None in the function create_custom_user"
                return
        if backend.__class__ != FacebookBackend:
                return

        res = kwargs['response']

        print "Getting/Updating data for userid " + res.get('id')

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
		print "Email not found for user " + str(res.get('id')) + ". Using " + profile.email
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.gender = genderdict[res.get('gender') or "not specified"]
        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name')
        if res.get('location'):
                profile.location = res.get('location').get('name')
        profile.username = res.get('username')
        profile.userid = res.get('id')

        print "----"

        graph = GraphAPI(res.get('access_token'))
        responsegraph = graph.get(str(res['id'])+'?fields=birthday')
        profile.birthday = str(responsegraph.get('birthday'))

        profile.save()

        print "----"

        userloggedin = UserTomonotomo.objects.get(userid=res['id'])

        userlogin = UserLogin()
        userlogin.userlogin = userloggedin
        userlogin.save()

        print "----"

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

	print "----"

	try:
		userquota = UserQuota.objects.get(userid=res.get('id'))
	except UserQuota.DoesNotExist:
		userquota = UserQuota()
		userquota.userid = res.get('id')
		userquota.quota=30
		userquota.save()

	print "----"

	if kwargs['is_new']==False:
		print "completed for returning user " + str(res.get('id'))
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
                profilefriends.save()

        print "----"

        print "completed for first time user " + str(userloggedin)
        return

def getSanitizedEducation (educationProfile):
        """ Helper function to get education profile as a structured string """
        education = ""
        for value in educationProfile:
                if value.get('school') and value['school'].get('name'):
                        education = education + value['school']['name']+'---'
                #if value.get('concentration'):
                #        for concentration in value['concentration']:
                #                education = education + concentration['name']+'---'
        return education

def getSanitizedWork (workProfile):
        """ Helper function to get work profile as a structured string """
        work = ""
        for value in workProfile:
                if value.get('employer') and value['employer'].get('name'):
                        work = work + value['employer']['name']+'---'
        return work

def postProcessing(userid, accessToken):

	userloggedin = UserTomonotomo.objects.get(userid=userid)
        graph = GraphAPI(accessToken)
        print "processing " + accessToken
	try:
		## Checking if accesstoken is valid
        	friendnumber = graph.fql('SELECT friend_count FROM user where uid=me()')
        	numberfriends = friendnumber.get('data')[0].get('friend_count')
        	print "number of friends " + str(numberfriends)
	except Exception as e:
		print e
		raise

        friendgraphdata= []
        friendgraph= []
        for i in range(0,10):
            query = 'SELECT uid,first_name,last_name,username,name,birthday,education,work,sex,hometown_location,current_location FROM user WHERE uid in (SELECT uid2 FROM friend where uid1=me() limit '+str(max(0,(i*500)-100))+',500)'
            friendgraphdata.append(graph.fql(query))
            friendgraph.extend(friendgraphdata[i].get('data'))
            print "received data for " + str(len(friendgraph)) + " friends - some are duplicate"

        print "list of friends data "+str(len(friendgraph))+" - some are duplicate"

        count = 0
        for frienddata in friendgraph:

            count = count + 1
            print "Saving detailed information for friendid - " + str(frienddata.get('uid')) + " - count " + str(count)

            try:
		profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=frienddata.get('uid'))
            except UserFriends.DoesNotExist:
                profilefriends = UserFriends()
                profilefriends.userid = userloggedin
                profilefriends.friendid = frienddata.get('uid')
                profilefriends.save()
	    except Exception as e:
	    	print "Exception saving UserFriends"
		print e
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

            	userfriend.username = frienddata.get('username')
            	userfriend.userid = frienddata.get('uid')
            
	    	if frienddata.get('birthday'):
                	try:
                    		userfriend.birthday = time.strftime("%m/%d/%Y", time.strptime(frienddata.get('birthday'), "%B %d, %Y"))
                	except:
                    		print "could not parse birthday for " + str(frienddata.get('uid'))

	    except Exception as e:
		print "Exception getting information"
		print e
		raise

	    try:
            	userfriend.save()
	    except Exception as inst:
		print "Exception saving UserData"
		print inst
		raise

	print "!!!!!!!!!"

        return

class startPostProcessing(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'tomonotomo.social_auth_pipeline.startPostProcessing'    # a unique code

    def do(self):
	print "StartPostProcessing starts"
        pendingusers = UserProcessing.objects.all().values('userloggedin','accesstoken')
	print "StartPostProcessing starts - length of list is " + str(len(pendingusers)) 
        if len(pendingusers) > 0:
        	randnum = randint(0, len(pendingusers)-1)
		userloggedin = pendingusers[randnum].get('userloggedin')
                accesstoken = pendingusers[randnum].get('accesstoken')
                try:
			print "Starting Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken
                	postProcessing(userloggedin, accesstoken)
			print "Almost Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken
                	UserProcessing.objects.filter(userloggedin = userloggedin).delete()
                	print "Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken
        	except:
            		print "Failed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken

		print "Before this operation - length of list was " + str(len(pendingusers))

    	return

class updateQuota(CronJobBase):
	RUN_AT_TIMES = ['00:00']
	schedule = Schedule(run_at_times=RUN_AT_TIMES)
	code='tomonotomo.social_auth_pipeline.updateQuota'

	def do(self):
		print "UpdateQuota starts"
		users = UserTomonotomo.objects.all().exclude(email=None).values('userid')
		for user in users:
			try:
                		userquota = UserQuota.objects.get(userid=user['userid'])
				userquota.quota=30
        		except UserQuota.DoesNotExist:
                		userquota = UserQuota(userid=user['userid'], quota=30)
                	userquota.save()

		print "Done UpdateQuota"
		return

