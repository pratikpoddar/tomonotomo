from django.db import models


class UserTomonotomo(models.Model):
    userid= models.IntegerField(null=False, unique=True, db_index=True)
    email= models.CharField(max_length=100L)
    accesstoken= models.CharField(max_length=500L)
    expiresin= models.IntegerField(null=True)
    first_name= models.CharField(max_length=100L,null=True)
    last_name= models.CharField(max_length=100L,null=True)
    birthday= models.CharField(max_length=100L)
    hometown= models.CharField(max_length=100L)
    location= models.CharField(max_length=100L)
    gender= models.CharField(max_length=100L)
    interestedin= models.CharField(max_length=30)
    education= models.CharField(max_length=500L)
    work= models.CharField(max_length=500L)
    time= models.DateTimeField(null=True)
    username= models.CharField(max_length=200L, unique=True)
    
    ## TODO: Get Birthday, Friend List, Time of updation and Interested In

    def get_full_name(self):
            return self.first_name + " " + self.last_name
    def get_short_name(self):
            return self.first_name
