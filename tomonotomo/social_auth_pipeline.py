from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
import time

from tomonotomo.models import UserTomonotomo, UserFriends

from django.db import transaction

@transaction.commit_manually
def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        print "Creating Custom User"

        ## TODO: Make not updating condition stricter. stop only if (not new) and (updated in last 10 days)
        # if kwargs['is_new'] == False:
        #     print "Returning user " + str(user)
        #     transaction.commit()
        #     return

        print "Getting data for first time user " + str(user)

        if user is None:
                print "User came as None in the function create_custom_user"
                transaction.commit()
                return
        if backend.__class__ != FacebookBackend:
                transaction.commit()
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
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.gender = res.get('gender') or "not specified"
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

        transaction.commit()

        print "----"

        friendlist = graph.fql('SELECT uid2 FROM friend where uid=me() limit 5')
        print "Ffffffffffffffffffffffffffffffff"
        print friendlist
        print "ffffffffffffffffffffffffffqqqqqqqqqqqqqqqqqqqqq"


        userloggedin = UserTomonotomo.objects.get(userid=res['id'])

        print "----"

        friendnumber = graph.fql('SELECT friend_count FROM user where uid=me()')
        numberfriends = friendnumber.get('data')[0].get('friend_count')
        print "number of friends " + str(numberfriends)

        friendgraphdata= []
        friendgraph= []
        for i in range(0,10):
            query = 'SELECT uid,first_name,last_name,username,name,birthday,education,work,sex,hometown_location,current_location FROM user WHERE uid in (SELECT uid2 FROM friend where uid1=me() limit '+str(max(0,(i*500)-100))+',500)'
            friendgraphdata.append(graph.fql(query))
            friendgraph.extend(friendgraphdata[i].get('data'))
            print "recieved data for " + str(len(friendgraph)) + " friends - some are duplicate"

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

            try:
                userfriend = UserTomonotomo.objects.get(userid=frienddata.get('uid'))
            except UserTomonotomo.DoesNotExist:
                userfriend = UserTomonotomo()

            if frienddata.get('work'):
               userfriend.work= getSanitizedWork(frienddata['work'])
            if frienddata.get('education'):
                userfriend.education= getSanitizedEducation(frienddata['education'])
            userfriend.first_name = frienddata.get('first_name')
            userfriend.last_name = frienddata.get('last_name')
            userfriend.gender = frienddata.get('sex') or "not specified"
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

            userfriend.save()

            if count % 50 == 0:
                transaction.commit()

        transaction.commit()
        print "completed for " + str(userloggedin)
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

def postProcessing(accessToken):

        graph = GraphAPI(accessToken)
        print "processing " + accessToken
        friendnumber = graph.fql('SELECT friend_count FROM user where uid=me()')
        numberfriends = friendnumber.get('data')[0].get('friend_count')
        print "number of friends " + str(numberfriends)

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

            # try:
            #     profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=frienddata.get('uid'))
            # except UserFriends.DoesNotExist:
            #     profilefriends = UserFriends()
            #     profilefriends.userid = userloggedin
            #     profilefriends.friendid = frienddata.get('uid')
            #     profilefriends.save()

            try:
                userfriend = UserTomonotomo.objects.get(userid=frienddata.get('uid'))
            except UserTomonotomo.DoesNotExist:
                userfriend = UserTomonotomo()

            if frienddata.get('work'):
               userfriend.work= getSanitizedWork(frienddata['work'])
            if frienddata.get('education'):
                userfriend.education= getSanitizedEducation(frienddata['education'])
            userfriend.first_name = frienddata.get('first_name')
            userfriend.last_name = frienddata.get('last_name')
            userfriend.gender = frienddata.get('sex') or "not specified"
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

            userfriend.save()

        return
