# -*- coding: utf-8 -*-

import logging
import re

logger = logging.getLogger(__name__)

class Literals:
  def __init__(self, *literals):
    self.literals = []
    for literal in literals:
      if isinstance(literal, Literals):
        self.literals.extend(literal.literals)
      else:
        self.literals.append(literal)

    self.literals = sorted(set(self.literals))
    self.literals = {re.escape(l) : l for l in self.literals}
    self.pattern = '|'.join(self.literals)
    self.regex = re.compile(self.pattern, re.IGNORECASE)
    self.map = {l.lower() : l for l in self.literals}

  def matches(self, text):
    matches = self.regex.pattern != '' and self.regex.match(text) != None
    logger.debug("Match '%s' and text '%s': %s", self.regex.pattern, text, matches)
    return matches

  def convert(self, m):
    key = m.group(1)
    try:
      replacement = self.map[key.lower()]
    except KeyError:
      replacement = key

    # Don't lowercase words at the beginning of a title
    if m.start(1) == 0 and replacement[0:1].islower():
      replacement = key

    logger.debug('Literal %s => %s', key, replacement)
    return replacement

