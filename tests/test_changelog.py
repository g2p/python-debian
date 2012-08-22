#!/usr/bin/python
# vim: fileencoding=utf-8
#
# changelog.py -- Python module for Debian changelogs
# Copyright (C) 2006-7 James Westby <jw+debian@jameswestby.net>
# Copyright (C) 2008 Canonical Ltd.
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

# The parsing code is based on that from dpkg which is:
# Copyright 1996 Ian Jackson
# Copyright 2005 Frank Lichtenheld <frank@lichtenheld.de>
# and licensed under the same license as above.

from __future__ import absolute_import

import sys
import unittest

import six

sys.path.insert(0, '../lib/')

from debian import changelog


def open_utf8(filename, mode='r'):
    """Open a UTF-8 text file in text mode."""
    if sys.version < '3':
        return open(filename, mode=mode)
    else:
        return open(filename, mode=mode, encoding='UTF-8')


class ChangelogTests(unittest.TestCase):

    def test_create_changelog(self):
        f = open('test_changelog')
        c = f.read()
        f.close()
        cl = changelog.Changelog(c)
        cs = str(cl)
        clines = c.split('\n')
        cslines = cs.split('\n')
        for i in range(len(clines)):
            self.assertEqual(clines[i], cslines[i])
        self.assertEqual(len(clines), len(cslines), "Different lengths")

    def test_create_changelog_single_block(self):
        f = open('test_changelog')
        c = f.read()
        f.close()
        cl = changelog.Changelog(c, max_blocks=1)
        cs = str(cl)
        self.assertEqual(cs,
        """gnutls13 (1:1.4.1-1) unstable; urgency=HIGH

  [ James Westby ]
  * New upstream release.
  * Remove the following patches as they are now included upstream:
    - 10_certtoolmanpage.diff
    - 15_fixcompilewarning.diff
    - 30_man_hyphen_*.patch
  * Link the API reference in /usr/share/gtk-doc/html as gnutls rather than
    gnutls-api so that devhelp can find it.

 -- Andreas Metzler <ametzler@debian.org>  Sat, 15 Jul 2006 11:11:08 +0200

""")

    def test_modify_changelog(self):
        f = open('test_modify_changelog1')
        c = f.read()
        f.close()
        cl = changelog.Changelog(c)
        cl.package = 'gnutls14'
        cl.version = '1:1.4.1-2'
        cl.distributions = 'experimental'
        cl.urgency = 'medium'
        cl.add_change('  * Add magic foo')
        cl.author = 'James Westby <jw+debian@jameswestby.net>'
        cl.date = 'Sat, 16 Jul 2008 11:11:08 -0200'
        f = open('test_modify_changelog2')
        c = f.read()
        f.close()
        clines = c.split('\n')
        cslines = str(cl).split('\n')
        for i in range(len(clines)):
            self.assertEqual(clines[i], cslines[i])
        self.assertEqual(len(clines), len(cslines), "Different lengths")

    def test_add_changelog_section(self):
        f = open('test_modify_changelog2')
        c = f.read()
        f.close()
        cl = changelog.Changelog(c)
        cl.new_block(package='gnutls14',
                version=changelog.Version('1:1.4.1-3'),
                distributions='experimental',
                urgency='low',
                author='James Westby <jw+debian@jameswestby.net>')

        self.assertRaises(changelog.ChangelogCreateError, cl.__str__)

        cl.set_date('Sat, 16 Jul 2008 11:11:08 +0200')
        cl.add_change('')
        cl.add_change('  * Foo did not work, let us try bar')
        cl.add_change('')

        f = open('test_modify_changelog3')
        c = f.read()
        f.close()
        clines = c.split('\n')
        cslines = str(cl).split('\n')
        for i in range(len(clines)):
            self.assertEqual(clines[i], cslines[i])
        self.assertEqual(len(clines), len(cslines), "Different lengths")

    def test_strange_changelogs(self):
        """ Just opens and parses a strange changelog """
        f = open('test_strange_changelog')
        c = f.read()
        f.close()
        cl = changelog.Changelog(c)

    def test_set_version_with_string(self):
        f = open('test_modify_changelog1')
        c1 = changelog.Changelog(f.read())
        f.seek(0)
        c2 = changelog.Changelog(f.read())
        f.close()
        c1.version = '1:2.3.5-2'
        c2.version = changelog.Version('1:2.3.5-2')
        self.assertEqual(c1.version, c2.version)
        self.assertEqual((c1.full_version, c1.epoch, c1.upstream_version,
                          c1.debian_version),
                         (c2.full_version, c2.epoch, c2.upstream_version,
                          c2.debian_version))

    def test_changelog_no_author(self):
        cl_no_author = """gnutls13 (1:1.4.1-1) unstable; urgency=low

  * New upstream release.

 --
"""
        c1 = changelog.Changelog()
        c1.parse_changelog(cl_no_author, allow_empty_author=True)
        self.assertEqual(c1.author, None)
        self.assertEqual(c1.date, None)
        self.assertEqual(c1.package, "gnutls13")
        c2 = changelog.Changelog()
        self.assertRaises(changelog.ChangelogParseError, c2.parse_changelog, cl_no_author)

    def test_magic_version_properties(self):
        f = open('test_changelog')
        c = changelog.Changelog(f)
        f.close()
        self.assertEqual(c.debian_version, '1')
        self.assertEqual(c.full_version, '1:1.4.1-1')
        self.assertEqual(c.upstream_version, '1.4.1')
        self.assertEqual(c.epoch, '1')
        self.assertEqual(str(c.version), c.full_version)

    def test_allow_full_stops_in_distribution(self):
        f = open('test_changelog_full_stops')
        c = changelog.Changelog(f)
        f.close()
        self.assertEqual(c.debian_version, None)
        self.assertEqual(c.full_version, '1.2.3')
        self.assertEqual(str(c.version), c.full_version)

    def test_str_consistent(self):
        # The parsing of the changelog (including the string representation)
        # should be consistent whether we give a single string, a list of
        # lines, or a file object to the Changelog initializer
        f = open('test_changelog')
        cl_data = f.read()
        f.seek(0)
        c1 = changelog.Changelog(f)
        f.close()
        c2 = changelog.Changelog(cl_data)
        c3 = changelog.Changelog(cl_data.splitlines())
        for c in (c1, c2, c3):
            self.assertEqual(str(c), cl_data)

    def test_utf8_encoded_file_input(self):
        f = open_utf8('test_changelog_unicode')
        c = changelog.Changelog(f)
        f.close()
        u = six.text_type(c)
        expected_u = six.u("""haskell-src-exts (1.8.2-3) unstable; urgency=low

  * control: Use versioned Replaces: and Conflicts:

 -- Marco T\xfalio Gontijo e Silva <marcot@debian.org>  Wed, 05 May 2010 18:01:53 -0300

haskell-src-exts (1.8.2-2) unstable; urgency=low

  * debian/control: Rename -doc package.

 -- Marco T\xfalio Gontijo e Silva <marcot@debian.org>  Tue, 16 Mar 2010 10:59:48 -0300
""")
        self.assertEqual(u, expected_u)
        self.assertEqual(bytes(c), u.encode('utf-8'))

    def test_unicode_object_input(self):
        f = open('test_changelog_unicode', 'rb')
        c_bytes = f.read()
        f.close()
        c_unicode = c_bytes.decode('utf-8')
        c = changelog.Changelog(c_unicode)
        self.assertEqual(six.text_type(c), c_unicode)
        self.assertEqual(bytes(c), c_bytes)

    def test_non_utf8_encoding(self):
        f = open('test_changelog_unicode', 'rb')
        c_bytes = f.read()
        f.close()
        c_unicode = c_bytes.decode('utf-8')
        c_latin1_str = c_unicode.encode('latin1')
        c = changelog.Changelog(c_latin1_str, encoding='latin1')
        self.assertEqual(six.text_type(c), c_unicode)
        self.assertEqual(bytes(c), c_latin1_str)
        for block in c:
            self.assertEqual(bytes(block),
                             six.text_type(block).encode('latin1'))

    def test_block_iterator(self):
        f = open('test_changelog')
        c = changelog.Changelog(f)
        f.close()
        self.assertEqual([str(b) for b in c._blocks], [str(b) for b in c])

    def test_len(self):
        f = open('test_changelog')
        c = changelog.Changelog(f)
        f.close()
        self.assertEqual(len(c._blocks), len(c))

class VersionTests(unittest.TestCase):

    def _test_version(self, full_version, epoch, upstream, debian):
        v = changelog.Version(full_version)
        self.assertEqual(v.full_version, full_version, "Full version broken")
        self.assertEqual(v.epoch, epoch, "Epoch broken")
        self.assertEqual(v.upstream_version, upstream, "Upstram broken")
        self.assertEqual(v.debian_version, debian, "Debian broken")

    def testversions(self):
        self._test_version('1:1.4.1-1', '1', '1.4.1', '1')
        self._test_version('7.1.ds-1', None, '7.1.ds', '1')
        self._test_version('10.11.1.3-2', None, '10.11.1.3', '2')
        self._test_version('4.0.1.3.dfsg.1-2', None, '4.0.1.3.dfsg.1', '2')
        self._test_version('0.4.23debian1', None, '0.4.23debian1', None)
        self._test_version('1.2.10+cvs20060429-1', None,
                '1.2.10+cvs20060429', '1')
        self._test_version('0.2.0-1+b1', None, '0.2.0', '1+b1')
        self._test_version('4.3.90.1svn-r21976-1', None,
                '4.3.90.1svn-r21976', '1')
        self._test_version('1.5+E-14', None, '1.5+E', '14')
        self._test_version('20060611-0.0', None, '20060611', '0.0')
        self._test_version('0.52.2-5.1', None, '0.52.2', '5.1')
        self._test_version('7.0-035+1', None, '7.0', '035+1')
        self._test_version('1.1.0+cvs20060620-1+2.6.15-8', None,
            '1.1.0+cvs20060620-1+2.6.15', '8')
        self._test_version('1.1.0+cvs20060620-1+1.0', None,
                '1.1.0+cvs20060620', '1+1.0')
        self._test_version('4.2.0a+stable-2sarge1', None, '4.2.0a+stable',
                           '2sarge1')
        self._test_version('1.8RC4b', None, '1.8RC4b', None)
        self._test_version('0.9~rc1-1', None, '0.9~rc1', '1')
        self._test_version('2:1.0.4+svn26-1ubuntu1', '2', '1.0.4+svn26',
                           '1ubuntu1')
        self._test_version('2:1.0.4~rc2-1', '2', '1.0.4~rc2', '1')
        self.assertRaises(
            ValueError, changelog.Version, 'a1:1.8.8-070403-1~priv1')

    def test_version_updating(self):
        v = changelog.Version('1:1.4.1-1')

        v.debian_version = '2'
        self.assertEqual(v.debian_version, '2')
        self.assertEqual(v.full_version, '1:1.4.1-2')

        v.upstream_version = '1.4.2'
        self.assertEqual(v.upstream_version, '1.4.2')
        self.assertEqual(v.full_version, '1:1.4.2-2')

        v.epoch = '2'
        self.assertEqual(v.epoch, '2')
        self.assertEqual(v.full_version, '2:1.4.2-2')

        self.assertEqual(str(v), v.full_version)

        v.full_version = '1:1.4.1-1'
        self.assertEqual(v.full_version, '1:1.4.1-1')
        self.assertEqual(v.epoch, '1')
        self.assertEqual(v.upstream_version, '1.4.1')
        self.assertEqual(v.debian_version, '1')

if __name__ == '__main__':
    unittest.main()
