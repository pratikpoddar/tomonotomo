from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening, UserQuota, UserLogin, UserProcessing
from datetime import datetime
from tomonotomo import dbutils

def removeProfile (fbid):
	removeUser(fbid)
	UserProcessing.objects.filter(userloggedin=fbid).delete()
	UserFriends.objects.filter(userid=fbid).delete()
	UserFriends.objects.filter(friendid=fbid).delete()
	UserFeedback.objects.filter(userid=fbid).delete()
	UserLogin.objects.filter(userlogin=fbid).delete()	
	UserQuota.objects.filter(userid=fbid).delete()
	UserHappening.objects.filter(userid=fbid).delete()
	UserTomonotomo.objects.filter(userid=fbid).delete()
	UserEmail.objects.filter(userid=fbid).delete()
	UserEmail.objects.filter(friendid=fbid).delete()
	UserEmail.objects.filter(fofid=fbid).delete()
	return

def removeUser (fbid):
        UserProcessing.objects.filter(userloggedin=fbid).delete()
        UserFriends.objects.filter(userid=fbid).delete()
        UserFeedback.objects.filter(userid=fbid).delete()
        UserLogin.objects.filter(userlogin=fbid).delete()
        UserQuota.objects.filter(userid=fbid).delete()
        UserHappening.objects.filter(userid=fbid).delete()
	try:
		user = UserTomonotomo.objects.get(userid=fbid)
		user.email = None
		user.save()
	except:
		pass
        UserEmail.objects.filter(userid=fbid).delete()
        UserEmail.objects.filter(friendid=fbid).delete()
        UserEmail.objects.filter(fofid=fbid).delete()
        return

removeProfile(100001913079283)
removeProfile(10151679883390671)
removeProfile(1561929970)
removeProfile(1558461027)
removeProfile(100003841702982)

	
