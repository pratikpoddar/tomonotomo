from django.db import models
from django.contrib.auth.models import (
        BaseUserManager, AbstractBaseUser
)

class UserTomonotomoManager(BaseUserManager):
        def create_user(self, username, userid, email=None, password=None, first_name=None, last_name=None, **extra_fields):
                if not username or not userid:
                        raise ValueError('Users must have a username and userid')

                user = self.model(
                        username=username,
                        email=UserManager.normalize_email(email),
                        first_name=first_name or '',
                        last_name=last_name or '',
                        fbuserid=userid,
                )
                user.set_password(password)
                user.save(using=self._db)
                return user

class UserTomonotomo(models.Model):
    userid= models.IntegerField(null=False)
    fbuserid= models.IntegerField(null=False)
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

    objects = UserTomonotomoManager()   
   
    def get_full_name(self):
            return self.first_name + " " + self.last_name
    def get_short_name(self):
            return self.first_name
    @property
    def __unicode__(self):
            return self.first_name + " " + self.last_name

    @property
    def work_as_list(self):
            return self.work.split('---')
    @property
    def education_as_list(self):
            return self.education.split('---')
