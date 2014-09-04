# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
from telemetry.page import page as page_module
from telemetry.page import page_set as page_set_module


class ToughEnergyCasesPage(page_module.Page):

  def __init__(self, url, page_set):
    super(ToughEnergyCasesPage, self).__init__(url=url, page_set=page_set)
    self.credentials_path = 'data/credentials.json'

class CodePenPage(ToughEnergyCasesPage):

  def __init__(self, url, page_set):
    super(CodePenPage, self).__init__(url, page_set)
    self.credentials = 'codepen'


class GooglePage(ToughEnergyCasesPage):

  def __init__(self, url, page_set):
    super(GooglePage, self).__init__(
        url=url,
        page_set=page_set)
    self.credentials = 'google'

  def RunNavigateSteps(self, action_runner):
    action_runner.NavigateToPage(self)
    action_runner.WaitForJavaScriptCondition(
        'window.gmonkey !== undefined &&'
        'document.getElementById("gb") !== null')


class ToughEnergyCasesPageSet(page_set_module.PageSet):
  """Pages for measuring Chrome power draw."""

  def __init__(self):
    super(ToughEnergyCasesPageSet, self).__init__(
        archive_data_file='data/tough_energy_cases.json',
        bucket=page_set_module.PUBLIC_BUCKET,
        credentials_path='data/credentials.json')

    # Why: productivity, top google properties
    self.AddPage(GooglePage('https://mail.google.com/mail/', self))

    # Why: Image constantly changed in the background, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/eIutG', self))

    # Why: Image constantly changed in the background, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/zcDdv', self))

    # Why: CSS Animation, above the fold
    self.AddPage(CodePenPage(
         'http://codepen.io/testificate364/debug/nrbDc', self))

    # Why: CSS Animation, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/fhKCg', self))

    # Why: requestAnimationFrame, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/paJhg',self))

    # Why: requestAnimationFrame, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/yaosK', self))

    # Why: setTimeout animation, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/DLbxg', self))

    # Why: setTimeout animation, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/kFvpd', self))

    # Why: setInterval animation, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/lEhyw', self))

    # Why: setInterval animation, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/zhgBD', self))

    # Why: Animated GIF, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/jetyn', self))

    # Why: Animated GIF, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/Kvdxs', self))

    # Why: HTML5 video, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/lJAiH', self))

    # Why: HTML5 video, below the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/EFceH', self))

    # Why: PostMessage between frames, above the fold
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/pgBHu', self))

    # Why: Asynchronous XHR continually running
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/iwAfJ', self))

    # Why: Web Worker continually running
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/ckItK', self))

    # Why: flash video
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/cFEaD', self))

    # Why: Blank page in the foreground
    self.AddPage(CodePenPage(
        'http://codepen.io/testificate364/debug/HdIgr', self))
