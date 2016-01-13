from __future__ import print_function

import re
import os
import sys
from argparse import ArgumentParser

import django
from django.conf import settings


SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': None,
            'USER': None,
            'PASSWORD': None,
            'HOST': None,
        }
    },
}


def parse_args():
    desc = "Back-end tool to import photos to leeche."
    parser = ArgumentParser(prog="lychee-pyimporter", description=desc)

    parser.add_argument("--retina", "-r", action="store_true",
                        help="generate thumb sizex2 for retina screen support")
    parser.add_argument("--link", "-l", action="store_true",
                        help="using symlink instead copy of original photo "
                             "in big dir")
    parser.add_argument("lychee_dir", action="store",
                        help="Lychee install directory")

    return parser.parse_args()


def parse_db_conf(lychee_path):
    conf_path = os.path.join(lychee_path, "data", "config.php")
    db_django_conf = SETTINGS['DATABASES']['default']
    params = ["dbHost", "dbUser", "dbPassword", "dbName"]
    expr = r"\$(?P<param>{0}) \= '(?P<value>.*)'; \#.*"
    rgx = re.compile(expr.format("|".join(params)))

    for line in open(conf_path):
        res = rgx.match(line)
        if res is None:
            continue

        param = res.group("param")[2:].upper()
        value = res.group("value")
        db_django_conf[param] = value

    if any(v is None for v in iter(db_django_conf.values())):
        msg = "invalid db configuration some parameters are missing: %s"
        raise Exception(msg % db_django_conf)

    print("lychee database configuration successfully loaded from", conf_path)


def handle_import(config):
    uploads_dir = os.path.join(config.lychee_dir, "uploads")
    import_path = os.path.join(uploads_dir, "import")
    lossless_dir = os.path.join(uploads_dir, 'big')
    medium_dir = os.path.join(uploads_dir, 'medium')
    thumb_dir = os.path.join(uploads_dir, 'thumb')

    # currently only one level is supported
    #   lychee uploads dir
    #   ├── photo dir1
    #   │   ├── photo1.jpg
    #   │   ├── photo2.jpg
    #   │   ├── ...
    #   ├── photo dir2
    #   │   ├── ...

    for elt in os.listdir(import_path):
        dir_path = os.path.join(import_path, elt)
        if not os.path.isdir(dir_path):
            continue

        album = Album(elt)
        album.db.save()

        for elt in os.listdir(dir_path):
            photo_path = os.path.join(dir_path, elt)
            if os.path.isdir(photo_path):
                continue

            photo = Photo(photo_path, album.id)

            if photo.file_already_in_db():
                print("file", photo_path, "already in db", file=sys.stderr)
                continue

            if config.link:
                photo.link(lossless_dir)
            else:
                photo.copy(lossless_dir)

            photo.medium(medium_dir)
            photo.thumb(thumb_dir, config.retina)

            photo.db.save()

        nb_photo = LycheePhotos.objects.filter(album=album.id).count()
        if nb_photo == 0:
            LycheeAlbums.objects.get(id=album.id).delete()
            print("nothing to import from", album.db.title, file=sys.stderr)
            continue

        print("album", album.db.title, "succesfully created and", nb_photo,
              "has been imported in")


ARGS = parse_args()
parse_db_conf(ARGS.lychee_dir)

# setup django standalone model
settings.configure(**SETTINGS)
django.setup()

from pyimporter.models import LycheeAlbums, LycheePhotos
from pyimporter.core import Album, Photo
handle_import(ARGS)
