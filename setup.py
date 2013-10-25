#!/usr/bin/python

# Copyright (C) 2006 James Westby <jw+debian@jameswestby.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from setuptools import setup

setup(name='python-debian',
      version='0.1.22a2',
      description='Debian package related modules',
      url='http://packages.debian.org/sid/python-debian',
      package_dir={'': 'lib'},
      packages=['debian', 'debian_bundle'],
      py_modules=['deb822'],
      maintainer='Debian python-debian Maintainers',
      maintainer_email='pkg-python-debian-maint@lists.alioth.debian.org',
      install_requires=['six'],
     )
