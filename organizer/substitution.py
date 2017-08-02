# -*- coding: utf-8 -*-

import inspect
import logging
import re

logger = logging.getLogger(__name__)

class Substitution:
  def __init__(self, pattern, replacement, ext = None, flags = re.IGNORECASE|re.UNICODE):
    self.pattern = re.compile(pattern, flags=flags)
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
