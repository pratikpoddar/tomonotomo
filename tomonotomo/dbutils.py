from tomonotomo.models import UserTomonotomo, UserFriends

## TODO: Where should a file like this be placed?
def getMutualFriends (fbid1, fbid2):
        
        fblist1 = UserFriends.objects.filter(userid=fbid1).values('friendid')
        fblist2 = UserFriends.objects.filter(userid=fbid2).values('friendid')

        return list(set(map(lambda x: x['friendid'], fblist1)) & set(map(lambda x: x['friendid'], fblist2)))

def getFriendsofFriends (fbid):
        
        fofs = set()
        fblist = getFriendsonTnT (fbid)
        for friendid in fblist:
                fofs |= set(map(lambda x: x['friendid'], UserFriends.objects.filter(userid=friendid).values('friendid')))
        return list(fofs)

def getFullName (fbid):
        return UserTomonotomo.objects.get(userid=fbid).get_full_name()

def getFriendName (fbid):
        ## TODO: Assuming first name has the correct name - which is Ok
        return UserFriends.objects.filter(friendid=fbid)[0].friendname

def getFriendsonTnT (fbid):
        fblist1 = UserFriends.objects.filter(userid=fbid).values('friendid')
        fblist2 = UserTomonotomo.objects.values('userid')

        return list(set(map(lambda x: x['friendid'], fblist1)) & set(map(lambda x: x['userid'], fblist2)))

## TODO: Change the function to give good suggestions
def getRandFoF (fbid):
        return 717323242

## TODO Email

## Change friendid from 0 to something and make UI for it
def sendemailFriend (userid, fofid, friendid):
        return

def sendemailFoF (userid, fofid, mutualfriendlist):
        return
