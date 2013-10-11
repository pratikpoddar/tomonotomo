# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'UserEmail', fields ['userid']
        db.create_index(u'tomonotomo_useremail', ['userid'])

        # Adding index on 'UserTomonotomo', fields ['email']
        db.create_index(u'tomonotomo_usertomonotomo', ['email'])

        # Adding index on 'UserFriends', fields ['friendid']
        db.create_index(u'tomonotomo_userfriends', ['friendid'])


    def backwards(self, orm):
        # Removing index on 'UserFriends', fields ['friendid']
        db.delete_index(u'tomonotomo_userfriends', ['friendid'])

        # Removing index on 'UserTomonotomo', fields ['email']
        db.delete_index(u'tomonotomo_usertomonotomo', ['email'])

        # Removing index on 'UserEmail', fields ['userid']
        db.delete_index(u'tomonotomo_useremail', ['userid'])


    models = {
        u'tomonotomo.useremail': {
            'Meta': {'object_name': 'UserEmail'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'fofid': ('django.db.models.fields.BigIntegerField', [], {}),
            'friendid': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'})
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
            'friendid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
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
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True', 'db_index': 'True'}),
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