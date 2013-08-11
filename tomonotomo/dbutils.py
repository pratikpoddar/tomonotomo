from tomonotomo.models import UserTomonotomo, UserFriends

## TODO: Where should a file like this be placed?
def getMutualFriends (fbid1, fbid2):
        
        fblist1 = UserFriends.objects.filter(userid=fbid1).values('friendid')
        fblist2 = UserFriends.objects.filter(userid=fbid2).values('friendid')

        return list(set(map(lambda x: x['friendid'], fblist1)) & set(map(lambda x: x['friendid'], fblist1)))

def getFriendsofFriends (fbid):
        
        fofs = set()
        fblist = UserFriends.objects.filter(userid=fbid).values('friendid')
        for friendid in fblist:
                fofs |= set(map(lambda x: x['friendid'], UserFriends.objects.filter(userid=friendid['friendid']).values('friendid'))) 
        
        return list(fofs)

def getFullName (fbid):
        return UserTomonotomo.objects.get(userid=fbid).get_full_name()

def getFriendName (fbid):
        return UserFriends.objects.get(friendid=fbid).friendname

def getNumberofFriends (fbid):
        return UserFriends.objects.filter(userid=fbid).count()