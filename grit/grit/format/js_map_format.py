#!/usr/bin/python2.4
#
# Copyright (c) 2009 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Formats as a .js file using a map: <english text> -> <localized text>.
"""

import os
import re
import types

from grit import util
from grit.format import interface
from grit.node import io


class TopLevel(interface.ItemFormatter):
  """Writes out the required preamble for JS files."""

  def Format(self, item, lang='en', begin_item=True, output_dir='.'):
    """Format the JS file header."""
    assert isinstance(lang, types.StringTypes)
    if not begin_item:
      return ''
    else:
      return '''// Copyright %d Google Inc. All Rights Reserved.
// This file is automatically generated by GRIT.  Do not edit.
''' % (util.GetCurrentYear())


class StringTable(interface.ItemFormatter):
  """Writes out the string table."""

  def Format(self, item, lang='en', begin_item=True, output_dir='.'):
    if begin_item:
      return '''
// Check to see if already defined in current scope.
var localizedStrings = localizedStrings || {};
'''
    else:
      return '\n'


class Message(interface.ItemFormatter):
  """Writes out a single message."""

  def Format(self, item, lang='en', begin_item=True, output_dir='.'):
    """Format a single message."""
    if not begin_item:
      return ''

    from grit.node import message

    assert isinstance(lang, types.StringTypes)
    assert isinstance(item, message.MessageNode)

    en_message = item.ws_at_start + item.Translate('en') + item.ws_at_end
    # Remove position numbers from placeholders.
    en_message = re.sub(r'%\d\$([a-z])', r'%\1', en_message)
    # Escape double quotes.
    en_message = re.sub(r'"', r'\"', en_message)

    loc_message = item.ws_at_start + item.Translate(lang) + item.ws_at_end
    # Escape double quotes.
    loc_message = re.sub(r'"', r'\"', loc_message)

    return '\nlocalizedStrings["%s"] = "%s";' % (en_message, loc_message)
