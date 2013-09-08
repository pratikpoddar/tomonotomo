from django.db import models
from datetime import datetime

GENDER_CHOICES = (
    (1, 'male'),
    (2, 'female'),
    (3, 'not specified')
    )

class UserTomonotomo(models.Model):

    userid= models.BigIntegerField(null=False, unique=True, db_index=True)
    email= models.CharField(max_length=100L, null=True)
    accesstoken= models.TextField( null=True)
    expiresin= models.IntegerField(null=True)
    first_name= models.CharField(max_length=100L,null=True)
    last_name= models.CharField(max_length=100L,null=True)
    birthday= models.CharField(max_length=100L,null=True)
    hometown= models.CharField(max_length=100L)
    location= models.CharField(max_length=100L)
    gender= models.IntegerField(choices=GENDER_CHOICES, default=3)
    education= models.CharField(max_length=2000L)
    work= models.CharField(max_length=2000L)
    time= models.DateTimeField(auto_now_add=True, blank=True)
    username= models.CharField(max_length=200L,null=True)

    def get_full_name(self):
	    try:
	    	fullname = (self.first_name + " " + self.last_name).encode('ascii')
            	return fullname
	    except:
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

class UserFriends(models.Model):
    userid= models.ForeignKey('UserTomonotomo', to_field='userid', null=False)
    friendid = models.BigIntegerField(null=False)

class UserFeedback(models.Model):
    userid= models.ForeignKey('UserTomonotomo', to_field='userid', null=False)
    fbid = models.BigIntegerField(null=False)
    action = models.IntegerField(null=False)

class UserProcessing(models.Model):
    userloggedin= models.ForeignKey('UserTomonotomo', to_field='userid', null=False)
    accesstoken = models.TextField(null=True)

class UserLogin(models.Model):
    userlogin = models.ForeignKey('UserTomonotomo', to_field='userid', null=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

class UserEmail(models.Model):
    userid = models.BigIntegerField(null=False)
    fofid = models.BigIntegerField(null=False)
    friendid = models.BigIntegerField(default=None, null=True)
    action = models.IntegerField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

