import sys
import argparse
import logging
import signal
from normalize.cleaner import *

def main():
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)

  parser = argparse.ArgumentParser(description = 'Normalizes files within a target directory by renaming them to a canonical form and sorting them into an output folder by media type.')
  parser.add_argument('directory', action='store', default='.', nargs='?', help='The input directory')
  parser.add_argument('-i', '--interactive', action='store_true', default=False, help='Request permission before renaming or moving a file')
  parser.add_argument('-l', '--log', action='store_true', default=False, help='Log output to file')
  parser.add_argument('-m', '--max-length', action='store', type=int,  default=140, metavar='len', help='The maximum filename length. Default is 140 characters.')
  parser.add_argument('-n', '--dry-run', action='store_true', default=False, help='Perform a trial run with no files renamed')
  parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Increase the verbosity level')
  parser.add_argument('-o', '--output', action='store', default='../organized/', metavar='dir', help='The output directory for the organized files')
  args = parser.parse_args()

  logfile = "normalize.log"
  level = logging.DEBUG if args.verbose else logging.INFO
  logger = logging.getLogger()
  logger.setLevel(level)

  consoleHandler = logging.StreamHandler(stream=sys.stdout)
  logger.addHandler(consoleHandler)

  if args.log:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]\t%(message)s")
    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

  FileCleaner(args).process()

