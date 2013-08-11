from django.db import models
from datetime import datetime

##TODO: Include foreign key to userid in the two tables
## TODO: If you are logging in for the second time, update and not add

GENDER_CHOICES = (
    ('male', 'male'),
    ('female', 'female'),
    ('not specified', 'not specified')
    )

class UserFriends(models.Model):
    userid= models.IntegerField(null=False)
    friendid = models.IntegerField(null=False)
    friendname = models.CharField(max_length=100L, null=True)
    friendgender = models.CharField(max_length=100L, choices=GENDER_CHOICES, default="not specified")

class UserTomonotomo(models.Model):

    userid= models.IntegerField(null=False, unique=True, db_index=True)
    email= models.CharField(max_length=100L)
    accesstoken= models.CharField(max_length=500L)
    expiresin= models.IntegerField(null=True)
    first_name= models.CharField(max_length=100L,null=True)
    last_name= models.CharField(max_length=100L,null=True)
    birthday= models.CharField(max_length=100L,null=True)
    hometown= models.CharField(max_length=100L)
    location= models.CharField(max_length=100L)
    gender= models.CharField(max_length=100L, choices=GENDER_CHOICES, default="not specified")
    interestedin= models.CharField(max_length=100L, null=True)
    education= models.CharField(max_length=500L)
    work= models.CharField(max_length=500L)
    time= models.DateTimeField(auto_now_add=True, blank=True)
    username= models.CharField(max_length=200L, unique=True)
    friends = models.CharField(max_length=1000L)
    
    ## TODO: Enter Interested In and update data if required

    def get_full_name(self):
            return self.first_name + " " + self.last_name
    def get_short_name(self):
            return self.first_name
    def get_age(self):
        if self.birthday:
            d2 = datetime.strptime(self.birthday, '%m/%d/%Y').date()
            d1 = datetime.now().date()
            return (d1-d2).days/365
        else:
            return None

class UserFeedback(models.Model):
    userid= models.IntegerField(null=False)
    fbidid = models.IntegerField(null=False)
    action = models.IntegerField(null=False)
    actionText = models.CharField(max_length=1000L, null=True)


