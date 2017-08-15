#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def write_log(folder, filename, string):
  with open(os.path.join(folder, filename), 'a') as logfile:
      logfile.write(string + '\n')

def create_log(folder, filename):
  with open(os.path.join(folder, filename), 'w') as logfile:
    logfile.write('LOG:\n')