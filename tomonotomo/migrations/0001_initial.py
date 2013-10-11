# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserTomonotomo'
        db.create_table(u'tomonotomo_usertomonotomo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.BigIntegerField')(unique=True, db_index=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100L, null=True)),
            ('accesstoken', self.gf('django.db.models.fields.TextField')(null=True)),
            ('expiresin', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100L, null=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100L, null=True)),
            ('birthday', self.gf('django.db.models.fields.CharField')(max_length=100L, null=True)),
            ('hometown', self.gf('django.db.models.fields.CharField')(max_length=100L)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100L)),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('relstatus', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('education', self.gf('django.db.models.fields.CharField')(max_length=2000L)),
            ('work', self.gf('django.db.models.fields.CharField')(max_length=2000L)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=200L, null=True)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserTomonotomo'])

        # Adding model 'UserFriends'
        db.create_table(u'tomonotomo_userfriends', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tomonotomo.UserTomonotomo'], to_field='userid')),
            ('friendid', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'tomonotomo', ['UserFriends'])

        # Adding model 'UserFeedback'
        db.create_table(u'tomonotomo_userfeedback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tomonotomo.UserTomonotomo'], to_field='userid')),
            ('fbid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserFeedback'])

        # Adding model 'UserProcessing'
        db.create_table(u'tomonotomo_userprocessing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userloggedin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tomonotomo.UserTomonotomo'], to_field='userid')),
            ('accesstoken', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserProcessing'])

        # Adding model 'UserLogin'
        db.create_table(u'tomonotomo_userlogin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userlogin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tomonotomo.UserTomonotomo'], to_field='userid')),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserLogin'])

        # Adding model 'UserEmail'
        db.create_table(u'tomonotomo_useremail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.BigIntegerField')()),
            ('fofid', self.gf('django.db.models.fields.BigIntegerField')()),
            ('friendid', self.gf('django.db.models.fields.BigIntegerField')(default=None, null=True)),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserEmail'])

        # Adding model 'UserHappening'
        db.create_table(u'tomonotomo_userhappening', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.BigIntegerField')()),
            ('action', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'tomonotomo', ['UserHappening'])

        # Adding model 'UserQuota'
        db.create_table(u'tomonotomo_userquota', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('quota', self.gf('django.db.models.fields.IntegerField')(default=30)),
        ))
        db.send_create_signal(u'tomonotomo', ['UserQuota'])


    def backwards(self, orm):
        # Deleting model 'UserTomonotomo'
        db.delete_table(u'tomonotomo_usertomonotomo')

        # Deleting model 'UserFriends'
        db.delete_table(u'tomonotomo_userfriends')

        # Deleting model 'UserFeedback'
        db.delete_table(u'tomonotomo_userfeedback')

        # Deleting model 'UserProcessing'
        db.delete_table(u'tomonotomo_userprocessing')

        # Deleting model 'UserLogin'
        db.delete_table(u'tomonotomo_userlogin')

        # Deleting model 'UserEmail'
        db.delete_table(u'tomonotomo_useremail')

        # Deleting model 'UserHappening'
        db.delete_table(u'tomonotomo_userhappening')

        # Deleting model 'UserQuota'
        db.delete_table(u'tomonotomo_userquota')


    models = {
        u'tomonotomo.useremail': {
            'Meta': {'object_name': 'UserEmail'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'fofid': ('django.db.models.fields.BigIntegerField', [], {}),
            'friendid': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'tomonotomo.userfeedback': {
            'Meta': {'object_name': 'UserFeedback'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'fbid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tomonotomo.UserTomonotomo']", 'to_field': "'userid'"})
        },
        u'tomonotomo.userfriends': {
            'Meta': {'object_name': 'UserFriends'},
            'friendid': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tomonotomo.UserTomonotomo']", 'to_field': "'userid'"})
        },
        u'tomonotomo.userhappening': {
            'Meta': {'object_name': 'UserHappening'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userid': ('django.db.models.fields.BigIntegerField', [], {})
        },
        u'tomonotomo.userlogin': {
            'Meta': {'object_name': 'UserLogin'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userlogin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tomonotomo.UserTomonotomo']", 'to_field': "'userid'"})
        },
        u'tomonotomo.userprocessing': {
            'Meta': {'object_name': 'UserProcessing'},
            'accesstoken': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userloggedin': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tomonotomo.UserTomonotomo']", 'to_field': "'userid'"})
        },
        u'tomonotomo.userquota': {
            'Meta': {'object_name': 'UserQuota'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quota': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'userid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'})
        },
        u'tomonotomo.usertomonotomo': {
            'Meta': {'object_name': 'UserTomonotomo'},
            'accesstoken': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'birthday': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '2000L'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True'}),
            'expiresin': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True'}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'hometown': ('django.db.models.fields.CharField', [], {'max_length': '100L'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100L'}),
            'relstatus': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '200L', 'null': 'True'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '2000L'})
        }
    }

    complete_apps = ['tomonotomo']