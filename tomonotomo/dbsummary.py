from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback

def getSummary ():
        
        print "Number of Users with accesstoken: " + str(UserTomonotomo.objects.filter(accesstoken!='').count())
	print "Number of Users with email: " + str(UserTomonotomo.objects.filter(email!='').count())
	print "Number of Users with data: " + str(UserTomonotomo.objects.count())
	print "Number of UserFriend Entries: " + str(UserFriends.objects.count())
	print "Number of Feedback received: " + str(UserFeedback.objects.count())

	print "Users Registered: "
	print UserTomonotomo.objects.filter(email!='').values('first_name','last_name','userid')

	print "Feedback Sent: "
	print UserFeedback.objects.all().values()

        return

