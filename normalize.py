#!/usr/bin/env python3

import os
import re
import string
import sys
import argparse
import inspect
import logging
import readline
import signal

try:
  from titlecase import titlecase
except:
  print("titlecase package required: python -m pip install titlecase")
  exit(1)

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

parser = argparse.ArgumentParser(description = 'Normalizes files within a target directory by renaming them to a canonical form.')
parser.add_argument('directory', action='store', default='.', nargs='?', help='The target directory')
parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Request permission before renaming file')
parser.add_argument('-l', '--log', action='store_true', default=False, help='Log output to file')
parser.add_argument('-m', '--max-length', action='store', type=int,  default=140, metavar='len', help='The maximum filename length. Default is 140 characters.')
parser.add_argument('-n', '--dry-run', action='store_true', default=False, help='Perform a trial run with no files renamed')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Increase the verbosity level')
args = parser.parse_args()

logfile = "normalize.log"
level = logging.DEBUG if args.verbose else logging.INFO
logger = logging.getLogger()
logger.setLevel(level)

consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)
logger = logger.getChild(__name__)

if args.log:
  formatter = logging.Formatter("%(asctime)s [%(levelname)s]\t%(message)s")
  fileHandler = logging.FileHandler(logfile)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

class Normalization:
  def __init__(self, directory, file):
    self.directory = directory
    self.file = file
    if not os.path.isdir(file):
      self.name, self.extension = os.path.splitext(file)
    else:
      self.name = file
      self.extension = ''

  def getExtension(self):
    return self.extension[1:]

  def getName(self):
    return self.name

  def setName(self, name):
    if self.extension != '' and name.endswith(self.extension):
      self.name, ext = os.path.splitext(name)
    else:
      self.name = name.strip()

  def original(self, path=False):
    if path:
      return os.path.join(self.directory, self.file)
    else:
      return self.file

  def normalized(self, path=False):
    normalized = self.name + self.extension
    if path:
      return os.path.join(self.directory, normalized)
    else:
      return normalized

  def changed(self):
    return self.normalized() != self.file

class Literals:
  def __init__(self, *literals, copy=[]):
    self.literals = list(literals)
    for c in copy:
      self.literals.extend(c.literals)
    self.literals = sorted(set(self.literals))
    self.pattern = '|'.join(self.literals)
    self.regex = re.compile('|'.join(self.literals), re.IGNORECASE)
    self.map = {l.lower() : l for l in self.literals}

  def matches(self, text):
    matches = self.regex.pattern != '' and self.regex.match(text) != None
    logger.debug("Match '%s' and text '%s': %s", self.regex.pattern, text, matches)
    return matches

  def convert(self, m):
    key = m.group(1)
    replacement = self.map[key.lower()]
    logger.debug('Literal %s => %s', key, replacement)
    return replacement

class Substitution:
  def __init__(self, pattern, replacement, ext = None):
    self.pattern = re.compile(pattern, flags=re.IGNORECASE|re.UNICODE)
    self.replacement = replacement
    self.ext = ext

    if inspect.isfunction(self.replacement) or inspect.ismethod(self.replacement):
      self.display = "Substitution '%s' = lambda(m)" % self.pattern.pattern
    else:
      self.display = "Substitution '%s' = '%s'" % (self.pattern.pattern, self.replacement)

  def replace(self, normalization):
    name = normalization.getName()
    if self.ext == None or self.ext.matches(normalization.getExtension()):
      name = re.sub(self.pattern, self.replacement, name)
    logger.debug('%s => %s', self, name)
    normalization.setName(name)

  def __str__(self):
    return self.display

manga  = Literals("7z", "rar", "zip")
dir = Literals("")

abbreviations = Literals("Ave", "Bros", "Dr", "Jr", "Mr", "Mrs", "Ms", "Rev", "St", "vs")
acronyms = Literals("AKA", "C2C", "DC", "TV", "UFO", "UK", "USA")
foreign = Literals("al", "chan", "de", "du", "et", "ga", "kun", "ni", "-san", "und", "wa", "wo")
groups = Literals("CHD", "d'argh", "DCP", "DTG", "FTG", "HP", "JYK", "LGC", "LOL", "n0m1", "PSA", "QCF", "RARBG", "RMTeam", "UTR", "YSTeam")
metadata = Literals("1CH", "2CH", "6CH", "7CH", "AAC", "AC3", "azw3", "BluRay", "CD", "DL", "DTS", "DVD", "epub", "FLAC", "HDTV", "HEVC", "mobi", "MKV", "MP3", "pdf", "x264", "x265", "Xvid")
miscellaneous = Literals("C-3PO", "com", "iZombie")
numerals = Literals("II", "III", "IV", "VI", "VII", "VIII", "IX")
literals = Literals(copy=[acronyms, foreign, groups, metadata, miscellaneous, numerals])
possessives = Literals("Bob", "Marvel", "DC", "Childhood", "there", "Attenborough", "who")
small = Literals('a', 'an', 'and', 'as', 'at', 'but', 'by', 'en', 'for', 'if', 'in', 'of', 'on', 'or', 'the', 'to', 'via', 'vs\\.?')

ellipsis = Substitution(r'\. ?\. ?\.', r'…')
skippedFiles = set(['cover.jpg', 'metadata.opf', logfile])

preSubstitutions = [
  Substitution(r'(:|꞉|~)', '-'),                               # Replace colon and colon similars
  Substitution(r'(?<=\w)[-_]\s', ' - '),                     # Foo- Bar -> Foo - Bar
  Substitution(r'\s[_-](?=\w)', ' - '),                      # Foo -Bar -> Foo - Bar
  Substitution(r'\.(\w{3,4})$', r' \1', dir),                  # Folder Name.epub -> Folder Name epub
  Substitution(r'^([\[\(].*?[\]\)]) ?(.*)', r'\2 \1'),       # [HorribleSubs] Naruto 1.mkv -> Naruto 1 [HorribleSubs].mkv
  Substitution(r'(?<=[^\s])(\[|\()', r' \1'),                # Rambo(1988) -> Rambo (1988)
  Substitution(r'(\]|\))(?=[^\s,])', r'\1 '),                # [1988]Rambo -> [1988] Rambo
  Substitution(r'\[eds?\]', ''),                             # Book [ed] -> Book
  Substitution(r'\b(%s)s\b' % possessives.pattern, r"\1's"), # marvels -> Marvel's
  Substitution(r'\bDD(\d)\b', r'DD \1'),                     # DD5.1 -> DD 5.1
  Substitution(r'\bAAC(\d)\b', r'AAC \1'),                   # AAC1.0 -> AAC 1.0
  Substitution(r'\b[hx][ \.]?(26[45])\b', r'x\1'),           # H.265 -> x265
  Substitution(r'\b(%s)-' % metadata.pattern, r'\1 '),       # HEVC-RARBG -> HEVC RARBG
  Substitution(r'\bweb[- \.]?dl\b', r'Web-DL'),
  Substitution(r'\bweb[- \.]?rip\b', r'WebRip'),
  Substitution(r'\.(BD|BR|DVD)Rip\.', r' \1Rip '),
  Substitution(r'\bB(D|R)(Rip)?\b', r'BluRay'),
  Substitution(r'\(?epub\+\)?( request)?', ''),
  Substitution(r'\bx[ \.]files', r'X-Files'),
  Substitution(r'"', "'"),
  Substitution(r'[\?\*]', ''),
  Substitution(r'[<>\|\\_]', ' '),
  Substitution(r'\s+', ' ')
]

postSubstitutions = [
  Substitution(r'(- )?\bs?(\d\d)[\. ]?(e|x|ep)(\d\d)\b( -)?', r'S\2E\4'),           # s01e04 -> S01E04
  Substitution(r'(- )?\bs?(\d)[\. ]?[ex](\d\d)\b( -)?', r'S0\2E\3'),                # s01e04 -> S01E04
  Substitution(r'\b(\d)of\d\b', r'S01E0\1'),                                        # 4of6 -> S01E04
  Substitution(r'(^|(?<= ))(?:[a-z] ){2,}', lambda m: m.group(0).upper().replace(' ', '.') + ' '),  # A D -> A.D.
  Substitution(r'(?<=\b\d) (?=\d\b)', '.'),                                         # 5 1 -> 5.1
  Substitution(r'\b(%s) ' % abbreviations.pattern, r'\1. '),                        # Dr -> Dr.
  Substitution(r'\b(%s)\b' % literals.pattern, literals.convert),                   # [rmteam] -> [RMTeam]
  Substitution(r'\bV(ol(ume|\.)? ?)?(\d+)\b', r'v\3', manga),                       # Vol. 01 -> v01
  Substitution(r'\bV(\d+)\b', r'v\1'),                                              # V01 -> v01
  Substitution(r'\bC(h(apters?|\.)?)? ?(\d+)\b', r'c\3', manga),                    # Chapters 001 -> c001
  Substitution(r'\bC(\d+)\b', r'c\1'),                                              # C001 -> c001
  Substitution(r'\[[a-f0-9]{8}\]', lambda m: m.group(0).upper()),                   # [Eb6cb498] -> [EB6CB498]
  Substitution(r'(?<=[,\]\)\d] )(%s)' % small.pattern, lambda m: m.group(1).capitalize())   # Simpsons, the (2015) the -> Simpsons, The (2015) The
]

def normalize(normalization):
  ellipsis.replace(normalization)
  name = normalization.getName()

  if name.count(".") >= 3 and name.count(".") > name.count(" "):
    name = name.replace(".", " ")

  if name.count("-") > 3 and name.count(" ") == 0:
    name = name.replace("-", " ")

  if name.count("_") >= 2:
    name = name.replace("_", " ")

  normalization.setName(name)

  for substitution in preSubstitutions:
    substitution.replace(normalization)

  name = titlecase(normalization.getName())
  normalization.setName(name)

  logger.debug('Titlecase => %s', name)

  for substitution in postSubstitutions:
    substitution.replace(normalization)

def clean(normalization):
  logger.debug("Visiting %s", normalization.directory)
  confirm = False

  normalize(normalization)

  if len(normalization.normalized()) > args.max_length:
    logger.warn('Truncating filename: %s' % file)
    slice = args.max_length - 1 - len(normalization.extension)
    shortened = normalization.getName()[0:slice] + "…"
    normalization.setName(shortened)
    logger.warn('length: %s', len(normalization.normalized()))

  if normalization.changed():
    confirm = not args.dry_run
    logger.info('%s =>', normalization.original())
    logger.info('%s', normalization.normalized())

    if args.interactive:
      result = input(r"Rename file? (Yes/No/Edit) ").lower()
      confirm = result == 'y' or result == 'yes'

      if result == 'e' or result == 'edit':
        confirm = True
        readline.set_startup_hook(lambda: readline.insert_text(normalization.normalized()))
        normalization.setName(input())
        readline.set_startup_hook(None)

    if confirm:
      try:
        logger.debug("Renaming: %s", normalization.normalized(True))
        os.renames(normalization.original(True), normalization.normalized(True))
      except Exception as e:
        logger.error("Unable to rename: %s", e)

try:
  for directory, directories, files in os.walk(args.directory, topdown = False):
    for file in sorted(files):
      if file not in skippedFiles:
        clean(Normalization(directory, file))

    if directory != args.directory:
      parent, child = os.path.split(directory)
      clean(Normalization(parent, child))
except KeyboardInterrupt:
  pass

