from django.db import models
from datetime import datetime

GENDER_CHOICES = (
    (1, 'male'),
    (2, 'female'),
    (3, 'not specified')
    )

RELSTATUS_CHOICES = (
	(1, 'Single'),
	(2, 'Engaged/Married'),
	(3, 'not specified')
	)

class UserTomonotomo(models.Model):

    userid= models.BigIntegerField(null=False, unique=True, db_index=True)
    email= models.CharField(max_length=100L, null=True, db_index=True)
    accesstoken= models.TextField( null=True)
    expiresin= models.IntegerField(null=True)
    first_name= models.CharField(max_length=100L,null=True)
    last_name= models.CharField(max_length=100L,null=True)
    birthday= models.CharField(max_length=100L,null=True)
    hometown= models.CharField(max_length=100L)
    location= models.CharField(max_length=100L, db_index=True)
    gender= models.IntegerField(choices=GENDER_CHOICES, default=3)
    relstatus=models.IntegerField(choices=RELSTATUS_CHOICES, default=1)
    education= models.CharField(max_length=2000L)
    work= models.CharField(max_length=2000L)
    interests = models.TextField(default=None,null=True)
    time= models.DateTimeField(auto_now_add=True, blank=True)
    username= models.CharField(max_length=200L,null=True)

    def get_full_name(self):
	    try:
	    	#fullname = (self.first_name + " " + self.last_name).encode('ascii')
		fullname = (self.first_name + " " + self.last_name).encode('utf-8')
            	return fullname
	    except:
		logger.exception("Name Not Readable for " + str(self.userid))
		return "Name not Readable"
    def get_short_name(self):
            return self.first_name
    def get_age(self):
        if self.birthday:
            try:
                d2 = datetime.strptime(self.birthday, '%m/%d/%Y').date()
                d1 = datetime.now().date()

                return (d1-d2).days/365
            except:
                return "[Age N.A.]"
        else:
            return "[Age N.A.]"

class UserLocation(models.Model):
    locationid = models.BigIntegerField(null=False, unique=True, db_index=True)
    userlocation = models.CharField(max_length=100L, db_index=True)
    latitude = models.FloatField(null=True, db_index=True)
    longitude = models.FloatField(null=True, db_index=True)

class UserFriends(models.Model):
    userid= models.ForeignKey('UserTomonotomo', to_field='userid', null=False, db_index=True)
    friendid = models.BigIntegerField(null=False, db_index=True)
    class Meta:
        unique_together = (("userid", "friendid"),)

class UserFeedback(models.Model):
    userid= models.ForeignKey('UserTomonotomo', to_field='userid', null=False, db_index=True)
    fbid = models.BigIntegerField(null=False, db_index=True)
    action = models.IntegerField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class UserProcessing(models.Model):
    userloggedin= models.ForeignKey('UserTomonotomo', to_field='userid', null=False)
    accesstoken = models.TextField(null=True)
    entryaddtime = models.DateTimeField(auto_now_add=True, null=True, default=None)

class UserLogin(models.Model):
    userlogin = models.ForeignKey('UserTomonotomo', to_field='userid', null=False, db_index=True)
    friends = models.IntegerField(null=False, default=0)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class UserEmail(models.Model):
    userid = models.BigIntegerField(null=False, db_index=True)
    fofid = models.BigIntegerField(null=False, db_index=True)
    friendid = models.BigIntegerField(default=None, null=True)
    action = models.IntegerField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class UserHappening(models.Model):
    userid = models.BigIntegerField(null=False)
    action = models.IntegerField(null=False)

class UserQuota(models.Model):
    userid = models.BigIntegerField(null=False, db_index=True)
    quota = models.IntegerField(null=False, default=20)

class TomonotomoQuotes(models.Model):
    quote = models.TextField(null=False)

