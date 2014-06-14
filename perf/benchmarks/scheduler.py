# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from telemetry import test
from measurements import smoothness
import page_sets


@test.Disabled('linux')  # crbug.com/368767
class SchedulerToughSchedulingCases(test.Test):
  """Measures rendering statistics while interacting with pages that have
  challenging scheduling properties.

  https://docs.google.com/a/chromium.org/document/d/
      17yhE5Po9By0sCdM1yZT3LiUECaUr_94rQt9j-4tOQIM/view"""
  test = smoothness.Smoothness
  page_set = page_sets.ToughSchedulingCasesPageSet


# Pepper plugin is not supported on android.
@test.Disabled('android', 'win')  # crbug.com/384733
class SchedulerToughPepperCases(test.Test):
  """Measures rendering statistics while interacting with pages that have
  pepper plugins"""
  test = smoothness.Smoothness
  page_set = page_sets.ToughPepperCasesPageSet

  def CustomizeBrowserOptions(self, options):
    # This is needed for testing pepper plugin.
    options.AppendExtraBrowserArgs('--enable-pepper-testing')
