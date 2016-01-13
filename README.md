# Overview

Lychee-pyimporter is a python tool to import photo album to lychee.
Like lychee "import from server" mode but without any php and front-end
dependencies.

This tools supports python 2.6 to python 3.x. It uses django mysql API 
to do queries to the lychee database.

This tools creates database album and photo from added folder in Lychee
imports directory. And it handles photo convertion to thumbnail(200x200),
thumbnailx2 (400x400) and medium(1920x1080).

The database configuration is directly loaded from Lychee wordir.

# Install

First clone this project and install the requirements of this tool.

* python mysqlclient
* python PIL
* python django

```
# apt-get install libmysqlclient-dev python-pil
# pip install django mysqlclient
```

# Run

Call this tool with -h option to get more help.

```
$ lychee-pyimporter /my/lychee/workdir
```
