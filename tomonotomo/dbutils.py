from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback

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
        try:
                ## Assuming that names of all entries of friendid are same - which should be the case
                return UserFriends.objects.filter(friendid=fbid).distinct()[0].friendname
        except:
                return ""

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

def historyFeedback (userid1, userid2):

        # return {'deactivate': [1, 2, 4], 'info': ["checking 1", "checking 2", "checking 3"]}

        result1 = UserFeedback.objects.filter(userid=userid1, fbid=userid2)
        result2 = UserFeedback.objects.filter(userid=userid2, fbid=userid1)

        deactivate = []
        info = []

        print result1
        print result2
        print len(result1)
        print len(result2)

        if (len(result1) > 0) and (len(result2) == 0):

            if result1.values()[0]['action'] == 1:
                info.append("Sent Introduction Request to Friends")

            if result1.values()[0]['action'] == 2:
                deactivate.append(2)
                deactivate.append(3)
                deactivate.append(4)
                info.append("Sent Direct Connection Request")

            if result1.values()[0]['action'] == 3:
                deactivate.append(3)
                deactivate.append(4)
                info.append("Cute, but don't connect")

            if result1.values()[0]['action'] == 4:
                deactivate.append(3)
                deactivate.append(4)
                info.append("Pass, and never show")

        if (len(result1) == 0) and (len(result2) > 0):

            if result2.values()[0]['action'] == 2:
                info.append("You would have received a Direct Connection Request over email")

        if (len(result1) > 0) and (len(result2) > 0):

            if (result2.values()[0]['action'] == 1) or (result2.values()[0]['action'] == 4):

                if result1.values()[0]['action'] == 1:
                    info.append("Sent Introduction Request to Friends")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Sent Direct Connection Request")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Cute, but don't connect")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Pass, and never show")

            if result2.values()[0]['action'] == 2:

                if result1.values()[0]['action'] == 1:
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Sent Introduction Request to Friends")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(1)
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Sent Direct Connection Request")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Cute, but don't connect")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Pass, and never show")
                    info.append("You would have received a Direct Connection Request over email")

            if result2.values()[0]['action'] == 3:

                if result1.values()[0]['action'] == 1:
                    info.append("Sent Introduction Request to Friends")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Sent Direct Connection Request")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Both of you find each other cute. Please connect")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Pass, and never show")

        return {'deactivate': deactivate, 'info': info}
