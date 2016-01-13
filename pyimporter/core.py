""" core part to handle lychee album and photo """

from __future__ import division

import os
import time
import hashlib
import mimetypes
from PIL import Image, ExifTags

from pyimporter.models import LycheeAlbums, LycheePhotos


ALLOWED_TYPES = ['jpeg', 'png', 'gif']
THUMB_SIZES = [(200, 200), (400, 400)]
MEDIUM_SIZE = (1920, 1080)
EXIF_ROTATION = {3: 180, 6: -90, 8: 90}


class Album(object):

    def __init__(self, title):
        self._id = 0
        self.db = LycheeAlbums(title=title, public=0, visible=1,
                               downloadable=0, sysstamp=int(time.time()))

    @property
    def id(self):
        if self._id == 0:
            self._id = LycheeAlbums.objects.get(title=self.db.title,
                                                sysstamp=self.db.sysstamp).id
        return self._id


class InvalidType(Exception):

    def __init__(self, path):
        types = ", ".join(ALLOWED_TYPES)
        msg = ("Photo type of {0} not supported, "
               "allowed types are {1}".format(path, types))
        super(InvalidType, self).__init__(msg)


class Photo(object):

    tags = {
        'ISOSpeedRatings': ('iso', lambda x: x),
        'FNumber': ('aperture', lambda x: 'f/{:.1f}'.format(x[0] / x[1])),
        'Make': ('make', lambda x: x),
        'Model': ('model', lambda x: x),
        'ExposureTime': ('shutter', lambda x: '{0}/{1} s'.format(x[0], x[1])),
        'FocalLength': ('focal', lambda x: '{:.2f} mm'.format(x[0] / x[1])),
        'DateTime': ('takestamp',
                     lambda x: time.mktime(time.strptime(x,
                                                         '%Y:%m:%d %H:%M:%S')))
    }

    def __init__(self, path, album=0):
        self.path = path
        basename = os.path.basename(path)
        title, self.ext = os.path.splitext(basename)
        self.ext = self.ext.lower()
        self.image = Image.open(self.path)

        fid, url = self.generate_filename()
        thumburl = "%s.jpeg" % fid
        checksum = self.generate_checksum()
        self.db = LycheePhotos(id=fid, title=title, album=album,
                               url=url, thumburl=thumburl, checksum=checksum,
                               public=0, star=0, medium=0)

        self.metadata()

        if self.db.type[self.db.type.index('/') + 1:] not in ALLOWED_TYPES:
            raise InvalidType(self.path)

    def __str__(self):
        fields = ""
        for k, v in iter(self.db.__dict__.items()):
            if not k.startswith('_'):
                fields += " {0}: {1}\n".format(k, v)
        return "db fields:\n%s" % fields

    def generate_filename(self):
        plain_id = ("%.4f" % time.time()).replace('.', '')
        crypted_id = hashlib.md5(plain_id.encode('utf-8')).hexdigest()
        url = "{0}{1}".format(crypted_id, self.ext)
        return plain_id, url

    def generate_checksum(self):
        with open(self.path, 'rb') as fd:
            sha1 = hashlib.sha1(fd.read())
        return sha1.hexdigest()

    def file_already_in_db(self):
        return len(LycheePhotos.objects.filter(checksum=self.db.checksum)) > 0

    def file_size_as_str(self):
        size = os.path.getsize(self.path)
        for unit in ['b', 'Kb', 'Mo']:
            if abs(size) < 1024.0:
                return "%3.1f %s" % (size, unit)
            size /= 1024.0
        return "%.1f %s" % (size, 'GB')

    def metadata(self):
        self.db.width, self.db.height = self.image.size
        self.db.type, _ = mimetypes.guess_type(self.path, False)
        self.db.size = self.file_size_as_str()
        exif = self.image._getexif() if hasattr(self.image, '_getexif') else {}

        for tag, value in iter(exif.items()):
            tag = ExifTags.TAGS.get(tag)
            if tag in self.tags:
                fieldname, formatter = self.tags[tag]
                setattr(self.db, fieldname, formatter(value))
            elif tag == 'Orientation':
                self.rotate(value)

    def rotate(self, orientation):
        degree = EXIF_ROTATION.get(orientation, None)
        if degree:
            self.image = self.image.rotate(degree)

    def copy(self, path):
        fullpath = os.path.join(path, self.db.url)
        self.image.save(fullpath, quality=100)

    def link(self, path):
        fullpath = os.path.join(path, self.db.url)
        os.symlink(self.path, fullpath)

    def medium(self, path):
        if self.image.size < MEDIUM_SIZE:
            return

        fullpath = os.path.join(path, self.db.url)
        photo = self.image.copy()
        photo.thumbnail(MEDIUM_SIZE, Image.ANTIALIAS)
        photo.save(fullpath, quality=100)
        self.db.medium = 1

    def thumb(self, path, retina=False):
        thumburl = os.path.join(path, self.db.thumburl)
        photo = self.image.copy()
        width, height = photo.size

        if width > height:
            left = int((width - height) / 2)
            right = height + left
            crop = (left, 0, right, height)
        else:
            upper = int((height - width) / 2)
            lower = width + upper
            crop = (0, upper, width, lower)

        photo = photo.crop(crop)
        photo.thumbnail(THUMB_SIZES[0], Image.ANTIALIAS)
        photo.save(thumburl, format="JPEG", quality=100)

        if retina:
            url = "{0}{1}".format(self.db.id, "@2x.jpeg")
            thumburl = os.path.join(path, url)
            photo = self.image.copy()
            photo = photo.crop(crop)
            photo.thumbnail(THUMB_SIZES[1], Image.ANTIALIAS)
            photo.save(thumburl, format="JPEG", quality=100)
