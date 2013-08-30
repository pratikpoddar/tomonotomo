from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback
from random import choice
import sendgrid

from functools32 import lru_cache

def getMutualFriends (fbid1, fbid2):
        
        fblist1 = UserFriends.objects.filter(userid=fbid1).values('friendid')
        fblist2 = UserFriends.objects.filter(friendid=fbid2).values('userid')

        return list(set(map(lambda x: x['friendid'], fblist1)) & set(map(lambda x: x['userid'], fblist2)))

@lru_cache(maxsize=16)
def getFriendsofFriends(fbid):
        
        fofs = set()
        fblist = getFriendsonTnT(fbid)
        for friendid in fblist:
                fofs |= set(map(lambda x: x['friendid'], UserFriends.objects.filter(userid=friendid['friendid']).values('friendid')))
        return list(fofs)

def getFullName (fbid):
        return UserTomonotomo.objects.get(userid=fbid).get_full_name()

def getFriendsonTnT (fbid):
        fblist = UserFriends.objects.filter(userid=fbid).values('friendid')
        fblist2 = filter(lambda x: UserTomonotomo.objects.get(userid=x['friendid']).email!=None, fblist)
        return fblist2

#TODO: Remove people with whom you have already had a conversation
def getRandFoF (fbid, reqgender):
        listofFoFs = getFriendsofFriends(fbid)

	friendlist = UserFriends.objects.filter(userid=fbid).values('friendid')
        listofFoFs = filter(lambda x: x not in friendlist, listofFoFs)

        fbidage = UserTomonotomo.objects.get(userid=fbid).get_age()

        if not reqgender == "indifferent":
            listofFoFs = filter(lambda x: UserTomonotomo.objects.get(userid=x).gender == reqgender, listofFoFs)

        if fbidage != "[Age N.A.]":
            listofFoFs = filter(lambda x: fbidage-5 <= UserTomonotomo.objects.get(userid=x).get_age() <= fbidage+5, listofFoFs)

        if len(listofFoFs):
            return choice(listofFoFs)
        else:
            return 0

## TODO: Improve Email

def sendemailCute (userid, fofid, mutualfriendlist):

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)

        # make a message object
        subject = "Tomonotomo - Connecting " + userinfo.first_name + " and " + fofinfo.first_name
        plaintext_message = "Both of you indicated that you find each other cute. Please take it forward from here. Both of you can see each other email addresses. You have following common friends."
        html_message = "Both of you indicated that you find each other cute. Please take it forward from here. Both of you can see each other email addresses. You have following common friends."
        message = sendgrid.Message("admin@tomonotomo.com", subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(fofinfo.email, fofinfo.get_full_name())

        # use the SMTP API to send your message
        #s.smtp.send(message)

        return

def sendemailFriend (userid, fofid, friendid):

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)
        friendinfo = UserTomonotomo.objects.get(userid=friendid)

        # make a message object
        subject = "Tomonotomo - Requesting to connect to " + fofinfo.first_name
        plaintext_message = "Please connect me to this friend of yours. His name is .... and his profile is ..."
        html_message = "Please connect me to this friend of yours. His name is .... and his profile is ..."
        message = sendgrid.Message("admin@tomonotomo.com", subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(friendinfo.email, friendinfo.get_full_name())

        # use the SMTP API to send your message
        #s.smtp.send(message)

        return

def sendemailFoF (userid, fofid, mutualfriendlist):

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)

        # make a message object
        subject = "Tomonotomo - Request to connect from " + userinfo.first_name
        plaintext_message = "I find you cute. I will like to take this forward. We have these common friends. What say?"
        html_message = "I find you cute. I will like to take this forward. We have these common friends. What say?"
        message = sendgrid.Message("admin@tomonotomo.com", subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(fofinfo.email, fofinfo.get_full_name())

        # use the SMTP API to send your message
        #s.smtp.send(message)

        return

def historyFeedback (userid1, userid2):

        # return {'deactivate': [1, 2, 4], 'info': ["checking 1", "checking 2", "checking 3"]}

        result1 = UserFeedback.objects.filter(userid=userid1, fbid=userid2)
        result2 = UserFeedback.objects.filter(userid=userid2, fbid=userid1)

        deactivate = []
        info = []

        if (len(result1) > 0) and (len(result2) == 0):

            if result1.values()[0]['action'] == 1:
                info.append("You have sent Introduction Request to Friends")

            if result1.values()[0]['action'] == 2:
                deactivate.append(1)
                deactivate.append(2)
                deactivate.append(3)
                deactivate.append(4)
                info.append("You have sent Direct Connection Request")

            if result1.values()[0]['action'] == 3:
                deactivate.append(3)
                deactivate.append(4)
                info.append("You marked - Looks Cute/Handsome")

            if result1.values()[0]['action'] == 4:
                deactivate.append(3)
                deactivate.append(4)
                info.append("You marked - Pass, and never show")

        if (len(result1) == 0) and (len(result2) > 0):

            if result2.values()[0]['action'] == 2:
                info.append("You would have received a Direct Connection Request over email. Best of Luck")

        if (len(result1) > 0) and (len(result2) > 0):

            if (result2.values()[0]['action'] == 1) or (result2.values()[0]['action'] == 4):

                if result1.values()[0]['action'] == 1:
                    info.append("You have sent Introduction Request to Friends")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(1)
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You have sent Direct Connection Request")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You marked - Looks Cute/Handsome")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You marked - Pass, and never show")

            if result2.values()[0]['action'] == 2:

                if result1.values()[0]['action'] == 1:
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You have sent Introduction Request to Friends")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(1)
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You have sent Direct Connection Request")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You marked - Looks Cute/Handsome")
                    info.append("You would have received a Direct Connection Request over email")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You marked - Pass, and never show")
                    info.append("You would have received a Direct Connection Request over email")

            if result2.values()[0]['action'] == 3:

                if result1.values()[0]['action'] == 1:
                    info.append("You have sent Introduction Request to Friends")

                if result1.values()[0]['action'] == 2:
                    deactivate.append(1)
                    deactivate.append(2)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You have sent Direct Connection Request")

                if result1.values()[0]['action'] == 3:
                    deactivate.append(1)
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("Both of you find each other cute/handsome. Tomonotomo sent an email to both of you. Best of Luck")

                if result1.values()[0]['action'] == 4:
                    deactivate.append(3)
                    deactivate.append(4)
                    info.append("You marked - Pass, and never show")

        return {'deactivate': deactivate, 'info': info}

