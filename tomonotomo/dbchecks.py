from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening, UserQuota, UserProcessing
import math
from django.db.models import Count

set11=set([])
set12=set([])
set2=set([])
set11 = set(map(lambda x: x['friendid'], UserFriends.objects.all().values('friendid')))
set12 = set(map(lambda x: x['userid'], UserFriends.objects.all().values('userid')))
set1 = set(list(set11)+list(set12))
set2 = set(map(lambda x: x['userid'], UserTomonotomo.objects.all().values('userid')))
print "------ Checking 1"
print "(UserFriends.userid + UserFriends.friendid) - UserTomonotomo.userid: " + str(set1-set2)
print "(UserFriends.userid) - UserTomonotomo.userid: " + str(set12-set2)
print "Both the above should be null"

list1=UserFeedback.objects.exclude(action=1).values('userid','fbid','action').annotate(Count('id'))
list2 = filter(lambda x: x['id__count'] > 1, list1)
print "----- Checking 2"
print len(list2)
print list2
print "The number should be zero"

list3=map(lambda x: str(x['userid'])+"-"+str(x['fbid']), UserFeedback.objects.filter(action=5).values('userid', 'fbid'))
list4=map(lambda x: str(x['userid'])+"-"+str(x['fbid']), UserFeedback.objects.exclude(action=5).values('userid','fbid'))
print "----- Checking 3"
print str(set(list3) & set(list4))
print "The above set should be empty"

list5=UserProcessing.objects.all()
print "----- Checking 4"
print list5
print "The above list should be empty"

list6=UserEmail.objects.filter(action__lt=100).values('userid','fofid','friendid','action').annotate(Count('id'))
list7=filter(lambda x: x['id__count']>1,list6)
print "----- Checking 5"
print list7
print "The above list should be empty"


