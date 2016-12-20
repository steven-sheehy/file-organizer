# -*- coding: utf-8 -*-

import os
import re
import string
import logging
import readline
import titlecase

import normalize.substitution
from normalize import config
from normalize.normalization import *

logger = logging.getLogger(__name__)

class FileCleaner:

  def __init__(self, args):
    self.args = args

  def process(self):
    try:
      for directory, directories, files in os.walk(self.args.directory, topdown = False):

        for dir in sorted(directories):
          self.clean(DirectoryNormalization(directory, dir))

        for file in sorted(files):
          if file not in config.skippedFiles:
            self.clean(FileNormalization(directory, file))
    except KeyboardInterrupt:
      pass

  def clean(self, normalization):
    original = normalization.original(True)
    logger.debug("Visiting: %s", original)
    confirm = False

    self.normalize(normalization)

    if normalization.changed():
      confirm = not self.args.dry_run
      logger.info('%s =>', normalization.original())
      logger.info('%s', normalization.normalized())

      if self.args.interactive and os.path.exists(original):
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
          os.renames(original, normalization.normalized(True))
        except Exception as e:
          logger.error("Unable to rename: %s", e)

  def normalize(self, normalization):
    name = normalization.getName()

    if name.count("-") > 3 and name.count(" ") == 0:
      name = name.replace("-", " ")

    if name.count("_") >= 2:
      name = name.replace("_", " ")

    normalization.setName(name)

    for substitution in config.preSubstitutions:
      substitution.replace(normalization)

    name = titlecase.titlecase(normalization.getName())
    normalization.setName(name)

    logger.debug('Titlecase => %s', name)

    for substitution in config.postSubstitutions:
      substitution.replace(normalization)

    name = normalization.normalized()
    if len(name) > self.args.max_length:
      slice = self.args.max_length - 1 - len(normalization.extension)
      shortened = normalization.getName()[0:slice] + "…"
      normalization.setName(shortened)
      logger.warning('Truncated filename length from %s to %s: %s', len(name), len(shortened), name)


