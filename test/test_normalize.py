#!/usr/bin/env python3
#
# python3 -m unittest discover

import unittest
from organizer.cleaner import *
from organizer.normalization import *

class TestCleaner(unittest.TestCase):

  def setUp(self):
    self.cleaner = FileCleaner(Args())

  def test_removed(self):
    self.assertRenamed('Foo*.mkv', 'Foo.mkv')
    self.assertRenamed('Foo?.mkv', 'Foo.mkv')
    self.assertRenamed('Foo.www.RapidMovieZ.com.mkv', 'Foo.mkv')
    self.assertRenamed('Foo (request).mkv', 'Foo.mkv')

  def test_ellipses(self):
    self.assertRenamed('Foo....mkv', 'Foo….mkv')
    self.assertRenamed('Foo . . . Bar.mkv', 'Foo … Bar.mkv')

  def test_periods(self):
    self.assertRenamed('Foo.epub', 'Foo epub', dir=True)
    self.assertUnchanged('06. Eazy-E - We Want Eazy (Feat. N.W.A. & the D.O.C.).mkv')
    self.assertRenamed('foo.s03e09.720p.5.1.webrip.hevc.x265.rmteam.mkv', 'Foo S03E09 720p 5.1 WebRip HEVC x265 RMTeam.mkv')
    self.assertUnchanged('.50 Foo.mkv')

  def test_literals(self):
    self.assertUnchanged('De Foo.mkv')
    self.assertRenamed('de foo.mkv', 'De Foo.mkv')
    self.assertRenamed('foo de bar.mkv', 'Foo de Bar.mkv')
    self.assertRenamed('i ii iii iv v vi vii viii ix x.mkv', 'I II III IV V VI VII VIII IX X.mkv')

  def test_acronym(self):
    self.assertUnchanged('A.B.C..mkv', 'A.B.C..mkv')
    self.assertUnchanged('(A.B.C.).mkv')
    self.assertUnchanged('Foo, A.B.C., Bar.mkv')
    self.assertUnchanged('FOO.A. Bar.mkv')

  def test_uppercase(self):
    self.assertUnchanged('INFIX.mkv')

  def test_dashes(self):
    self.assertRenamed('Foo- Bar.mkv', 'Foo - Bar.mkv')
    self.assertRenamed('Foo -Bar.mkv', 'Foo - Bar.mkv')
    self.assertRenamed('Foo-(Bar)-Baz.mkv', 'Foo - (Bar) - Baz.mkv')
    self.assertRenamed('Foo-[Bar]-Baz.mkv', 'Foo - [Bar] - Baz.mkv')
    self.assertRenamed('Foo:Bar.mkv', 'Foo - Bar.mkv')
    self.assertRenamed('Foo꞉Bar.mkv', 'Foo - Bar.mkv')
    self.assertRenamed('Foo~Bar.mkv', 'Foo - Bar.mkv')
    self.assertRenamed('Foo–Bar.mkv', 'Foo - Bar.mkv')
    self.assertUnchanged('Foo-bar.mkv')

  def test_parentheses(self):
    self.assertRenamed('(Foo)Bar.mkv', 'Bar (Foo).mkv')
    self.assertRenamed('Foo(Bar).mkv', 'Foo (Bar).mkv')

  def test_brackets(self):
    self.assertRenamed('[Foo]Bar.mkv', 'Bar [Foo].mkv')
    self.assertRenamed('Foo[Bar].mkv', 'Foo [Bar].mkv')

  def test_web_dl(self):
    self.assertRenamed('web-dl.mkv', 'Web-DL.mkv')
    self.assertRenamed('web dl.mkv', 'Web-DL.mkv')
    self.assertRenamed('web.dl.mkv', 'Web-DL.mkv')

  def test_webrip(self):
    self.assertRenamed('web rip.mkv', 'WebRip.mkv')
    self.assertRenamed('web.rip.mkv', 'WebRip.mkv')
    self.assertRenamed('web-rip.mkv', 'WebRip.mkv')

  def test_bluray(self):
    self.assertRenamed('bluray.mkv', 'BluRay.mkv')
    self.assertRenamed('brrip.mkv', 'BluRay.mkv')
    self.assertRenamed('bdrip.mkv', 'BluRay.mkv')

  def test_ed(self):
    self.assertRenamed('Foo [ed].mkv', 'Foo.mkv')

  def test_possessives(self):
    self.assertRenamed('marvels foo.mkv', 'Marvel\'s Foo.mkv')
    self.assertUnchanged('Marvels.mkv')
    self.assertUnchanged('Bobsled Burgers.mkv')

  def test_abbreviations(self):
    self.assertRenamed('Dr Who.mkv', 'Dr. Who.mkv')
    self.assertRenamed('DR Who.mkv', 'Dr. Who.mkv')

  def test_dd51(self):
    self.assertRenamed('Foo DD5.1.mkv', 'Foo DD 5.1.mkv')

  def test_aac(self):
    self.assertRenamed('AAC1.0.mkv', 'AAC 1.0.mkv')

  def test_x264(self):
    self.assertUnchanged('Foo x264.mkv')
    self.assertUnchanged('Foo x265.mkv')
    self.assertRenamed('Foo x.264.mkv', 'Foo x264.mkv')
    self.assertRenamed('Foo h.264.mkv', 'Foo x264.mkv')
    self.assertRenamed('Foo h 264.mkv', 'Foo x264.mkv')
    self.assertRenamed('Foo H264.mkv',  'Foo x264.mkv')
    self.assertRenamed('Foo x.265.mkv', 'Foo x265.mkv')
    self.assertRenamed('Foo h.265.mkv', 'Foo x265.mkv')
    self.assertRenamed('Foo h 265.mkv', 'Foo x265.mkv')
    self.assertRenamed('Foo H265.mkv',  'Foo x265.mkv')

  def test_volumes(self):
    self.assertRenamed('Foo V2.zip', 'Foo v2.zip')
    self.assertRenamed('Foo vol. 2.zip', 'Foo v2.zip')
    self.assertRenamed('Foo vol2.zip', 'Foo v2.zip')
    self.assertRenamed('Foo volume 2.zip', 'Foo v2.zip')
    self.assertRenamed('Foo vol 2.zip', 'Foo v2.zip')
    self.assertRenamed('Foo vol. a.zip', 'Foo Vol. A.zip')
    self.assertUnchanged('Foo Vol. 2.cbz')
    self.assertUnchanged('v2.zip')

  def test_chapters(self):
    self.assertRenamed('', '')
    self.assertUnchanged('c2.zip')

  def test_max_length(self):
    self.cleaner.args.max_length = 8
    self.assertRenamed('Foo Bar.mkv', 'Foo….mkv')

  def assertUnchanged(self, filename, dir=False):
    self.assertRenamed(filename, filename)

  def assertRenamed(self, filename, expected, dir=False):
    if dir:
      normalization = DirectoryNormalization('.', filename)
    else:
      normalization = FileNormalization('.', filename)

    self.cleaner.normalize(normalization)
    self.assertEqual(expected, normalization.normalized())

class Args:
  def __init__(self):
    self.max_length = 140
    self.interactive = False
    self.log = False
    self.dry_run = False
    self.verbose = False

if __name__ == '__main__':
  unittest.main()

