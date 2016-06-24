#!/usr/bin/env python3

from collections import Counter
import argparse
import logging
import os
import re
import sys

audio  = ["aac", "ape", "flac", "m4a", "m4p", "mka", "mp3", "oga", "ogg", "wma"]
books  = ["awz3", "awz", "chm", "djvu", "epub", "fb2", "htm", "html", "ibooks", "kf8", "lit", "mobi", "opf", "pdb", "pdf", "prc", "ps", "rtf"]
comics = ["cb7", "cba", "cbr", "cbt", "cbz"]
manga  = ["7z", "rar", "zip"]
video  = ["avi", "mkv", "m4v", "mov", "mp4", "mpeg", "mpg", "ogv", "qt", "rmvb", "vob", "webm", "wmv"]

parser = argparse.ArgumentParser(description = 'Organizes files by sorting them into an output folder by media type and other rules.')
parser.add_argument('directory', action='store', default='.', nargs='?', help='The input directory')
parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Request permission before moving a file')
parser.add_argument('-l', '--log', action='store_true', default=False, help='Log output to file')
parser.add_argument('-n', '--dry-run', action='store_true', default=False, help='Perform a trial run with no files moved')
parser.add_argument('-o', '--output', action='store', default='../organized/', metavar='dir', help='The output directory for the organized files')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Increase the verbosity level')
args = parser.parse_args()

level = logging.DEBUG if args.verbose else logging.INFO
logger = logging.getLogger()
logger.setLevel(level)

consoleHandler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(consoleHandler)
logger = logger.getChild(__name__)

if args.log:
  logfile = os.path.join(args.directory, "organizer.log")
  formatter = logging.Formatter("%(asctime)s [%(levelname)s]\t%(message)s")
  fileHandler = logging.FileHandler(logfile)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

class TypeMapping:
  def __init__(self, destination, extensions, pattern=""):
    self.destination = destination
    self.extensions = "|".join(sorted(set(extensions)))
    if pattern != "":
      self.pattern = re.compile("^.*%s.*\.(%s)$" % (pattern, self.extensions), re.I)
    else:
      self.pattern = re.compile("^.*\.(%s)$" % self.extensions, re.I)

  def matches(self, file):
    return self.pattern.match(file)

  def __str__(self):
    return "%s -> %s" % (self.pattern.pattern, self.destination)

class Organizer:
  def __init__(self):
    self.output = args.output
    self.unknownType = TypeMapping("unknown", "")
    self.typeMappings = [
      TypeMapping("books", books),
      TypeMapping("comics", comics),
      TypeMapping("manga", manga),
      TypeMapping("tv", video, r"S\d\dE\d\d"),
      TypeMapping("anime", video, r"(anime|deadfish|bakedfish|horriblesubs|1280x720 HEVC AAC|HEVC2|KamiFS|OVA|THORA)"),
      TypeMapping("movies", video),
      TypeMapping("music", audio)
    ]
    for mapping in self.typeMappings:
      logger.debug('Registered Type Mapping: %s', mapping)

  def fileType(self, file):
    for typeMapping in self.typeMappings:
      if typeMapping.matches(file):
        logger.debug("File mapped %s => %s", os.path.basename(file), typeMapping.destination)
        return typeMapping

    return self.unknownType

  def directoryType(self, dir):
    types = Counter()

    for root, dirs, files in os.walk(dir):
      for file in files:
        type = self.fileType(file)
        if type != self.unknownType:
          types[type] += 1

    for key in types:
      logger.debug('Count: %s = %s', key.destination, types[key])

    if len(types) > 0:
      return types.most_common(1)[0][0]
    else:
      return self.unknownType

  def process(self, source = args.directory):
    files = sorted(os.listdir(source))
    for file in files:
      self.processFile(os.path.join(source, file))

  def processFile(self, file):
    try:
      logger.debug("Processing: %s", file)
      if os.path.exists(file):
        destination = self.getDestination(file)
        confirm = not args.dry_run

        if args.interactive:
          result = input(r" (Y/N) ").lower()
          confirm = result == 'y' or result == 'yes'

        if confirm:
          os.renames(file, os.path.join(destination, os.path.basename(file)))
    except Exception as e:
      logger.error("Unable to rename: %s", e)

  def getDestination(self, file):
    if os.path.isdir(file):
      type = self.directoryType(file)
    else:
      type = self.fileType(file)

    logger.info('[%-6s] %s', type.destination, os.path.basename(file))
    return os.path.join(self.output, type.destination)

try:
  Organizer().process()
except KeyboardInterrupt:
  pass

