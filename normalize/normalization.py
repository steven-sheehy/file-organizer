# -*- coding: utf-8 -*-

import logging
import os

logger = logging.getLogger(__name__)

class Normalization:
  def __init__(self, directory, name):
    self.directory = directory
    self.originalName = name
    self.name = name

  def getExtension(self):
    return self.extension[1:]

  def getName(self):
    return self.name

  def setName(self, name):
    self.name = name.strip()

  def original(self, path=False):
    if path:
      return os.path.join(self.directory, self.originalName)
    else:
      return self.originalName

  def normalized(self, path=False):
    normalized = self.name + self.extension
    if path:
      return os.path.join(self.directory, normalized)
    else:
      return normalized

  def changed(self):
    return self.original() != self.normalized()


class FileNormalization(Normalization):
  def __init__(self, directory, name):
    super().__init__(directory, name)
    self.name, self.extension = os.path.splitext(name)

class DirectoryNormalization(Normalization):
  def __init__(self, directory, name):
    super().__init__(directory, name)
    self.extension = ''

