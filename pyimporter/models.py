# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class LycheeAlbums(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, null=True)
    sysstamp = models.IntegerField()
    public = models.IntegerField()
    visible = models.IntegerField()
    downloadable = models.IntegerField()
    password = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lychee_albums'
        app_label = 'lychee'


class LycheeLog(models.Model):
    time = models.IntegerField()
    type = models.CharField(max_length=11)
    function = models.CharField(max_length=100)
    line = models.IntegerField()
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lychee_log'
        app_label = 'lychee'


class LycheePhotos(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, null=True)
    url = models.CharField(max_length=100)
    tags = models.CharField(max_length=1000)
    public = models.IntegerField()
    type = models.CharField(max_length=10)
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.CharField(max_length=20)
    iso = models.CharField(max_length=15)
    aperture = models.CharField(max_length=20)
    make = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50)
    shutter = models.CharField(max_length=30)
    focal = models.CharField(max_length=20)
    takestamp = models.IntegerField(blank=True, null=True)
    star = models.IntegerField()
    thumburl = models.CharField(db_column='thumbUrl', max_length=50)  # Field name made lowercase.
    album = models.CharField(max_length=30)
    checksum = models.CharField(max_length=100, blank=True, null=True)
    medium = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'lychee_photos'
        app_label = 'lychee'


class LycheeSettings(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lychee_settings'
        app_label = 'lychee'

