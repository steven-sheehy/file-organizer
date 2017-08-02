import argparse
import logging
import signal
from organizer.cleaner import *

def main():
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)

  parser = argparse.ArgumentParser(description = 'Normalizes files within a target directory by renaming them to a canonical form and sorting them into an output folder by media type.')
  parser.add_argument('directory', action='store', default='.', nargs='?', help='The input directory')
  parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Request permission before renaming or moving a file')
  parser.add_argument('-l', '--log', action='store_true', default=False, help='Log output to file')
  parser.add_argument('-m', '--max-length', action='store', type=int,  default=140, metavar='len', help='The maximum filename length. Default is 140 characters')
  parser.add_argument('-n', '--dry-run', action='store_true', default=False, help='Perform a trial run with no files modified')
  parser.add_argument('-o', '--output', action='store', default='../organized/', metavar='dir', help='The output directory for the organized files')
  parser.add_argument('-s', '--semi-interactive', action='store_true', default=False, help='Manually confirm renaming the first file and automatically rename all other files in the same directory. Useful when a directory contains similarly named files. If the first file is edited or skipped, treat the rest of the folder as interactive.')
  parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Increase the verbosity level')
  args = parser.parse_args()

  FileCleaner(args).process()

