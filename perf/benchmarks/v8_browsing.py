# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import re

from core import perf_benchmark
from telemetry import benchmark
from telemetry import story
from telemetry.timeline import chrome_trace_config
from telemetry.timeline import chrome_trace_category_filter
from telemetry.web_perf import timeline_based_measurement
import page_sets


# Regex to filter out a few names of statistics supported by
# Histogram.getStatisticScalar(), see:
#   https://github.com/catapult-project/catapult/blob/d4179a05/tracing/tracing/value/histogram.html#L645  pylint: disable=line-too-long
_IGNORED_MEMORY_STATS_RE = re.compile(r'_(std|count|min|sum|pct_\d{4}(_\d+)?)$')

# Track only the high-level GC stats to reduce the data load on dashboard.
_IGNORED_V8_STATS_RE = re.compile(
    r'_(idle_deadline_overrun|percentage_idle|outside_idle)')
_V8_GC_HIGH_LEVEL_STATS_RE = re.compile(r'^v8-gc-('
    r'full-mark-compactor_|'
    r'incremental-finalize_|'
    r'incremental-step_|'
    r'latency-mark-compactor_|'
    r'memory-mark-compactor_|'
    r'scavenger_|'
    r'total_)')


class _v8BrowsingBenchmarkBaseClass(perf_benchmark.PerfBenchmark):
  """Base class for all v8 browsing benchmarks."""
  def CreateStorySet(self, options):
    return page_sets.SystemHealthStorySet(platform=self.PLATFORM, case='browse')


class _V8BrowsingBenchmark(_v8BrowsingBenchmarkBaseClass):
  """Base class for V8 browsing benchmarks.
  This benchmark measures memory usage with periodic memory dumps and v8 times.
  See browsing_stories._BrowsingStory for workload description.
  """

  def CreateCoreTimelineBasedMeasurementOptions(self):
    categories = [
      # Disable all categories by default.
      '-*',
      # Memory categories.
      'disabled-by-default-memory-infra',
      # EQT categories.
      'blink.user_timing',
      'loading',
      'navigation',
      'toplevel',
      # V8 categories.
      'blink.console',
      'disabled-by-default-v8.compile',
      'disabled-by-default-v8.gc',
      'renderer.scheduler',
      'v8',
      'webkit.console',
      # TODO(crbug.com/616441, primiano): Remove this temporary workaround,
      # which enables memory-infra V8 code stats in V8 code size benchmarks
      # only (to not slow down detailed memory dumps in other benchmarks).
      'disabled-by-default-memory-infra.v8.code_stats',
      # Blink categories.
      'blink_gc',
    ]
    options = timeline_based_measurement.Options(
        chrome_trace_category_filter.ChromeTraceCategoryFilter(
            ','.join(categories)))
    options.config.enable_android_graphics_memtrack = True
    # Trigger periodic light memory dumps every 1000 ms.
    memory_dump_config = chrome_trace_config.MemoryDumpConfig()
    memory_dump_config.AddTrigger('light', 1000)
    options.config.chrome_trace_config.SetMemoryDumpConfig(memory_dump_config)
    options.SetTimelineBasedMetrics([
      'expectedQueueingTimeMetric', 'v8AndMemoryMetrics', 'blinkGcMetric'])
    return options

  @classmethod
  def ValueCanBeAddedPredicate(cls, value, is_first_result):
    # TODO(crbug.com/610962): Remove this stopgap when the perf dashboard
    # is able to cope with the data load generated by TBMv2 metrics.
    if 'memory:chrome' in value.name:
      return ('renderer_processes' in value.name and
              not _IGNORED_MEMORY_STATS_RE.search(value.name))
    if 'v8-gc' in value.name:
      return (_V8_GC_HIGH_LEVEL_STATS_RE.search(value.name) and
              not _IGNORED_V8_STATS_RE.search(value.name))
    # Allow all other metrics.
    return True


class _V8RuntimeStatsBrowsingBenchmark(_v8BrowsingBenchmarkBaseClass):
  """Base class for V8 browsing benchmarks that measure RuntimeStats.
  RuntimeStats measure the time spent by v8 in different phases like
  compile, JS execute, runtime etc.,
  See browsing_stories._BrowsingStory for workload description.
  """

  def CreateCoreTimelineBasedMeasurementOptions(self):
    categories = [
      # Disable all categories by default.
      '-*',
      # Memory categories.
      'disabled-by-default-memory-infra',
      # UE categories requred by runtimeStatsTotalMetric to bucket
      # runtimeStats by UE.
      'rail',
      # EQT categories.
      'blink.user_timing',
      'loading',
      'navigation',
      'toplevel',
      # V8 categories.
      'blink.console',
      'disabled-by-default-v8.gc',
      'renderer.scheduler',
      'v8',
      'webkit.console',
      'disabled-by-default-v8.runtime_stats',
      # TODO(crbug.com/616441, primiano): Remove this temporary workaround,
      # which enables memory-infra V8 code stats in V8 code size benchmarks
      # only (to not slow down detailed memory dumps in other benchmarks).
      'disabled-by-default-memory-infra.v8.code_stats',
      # Blink categories.
      'blink_gc',
    ]
    options = timeline_based_measurement.Options(
        chrome_trace_category_filter.ChromeTraceCategoryFilter(
            ','.join(categories)))
    options.config.enable_android_graphics_memtrack = True
    # Trigger periodic light memory dumps every 1000 ms.
    memory_dump_config = chrome_trace_config.MemoryDumpConfig()
    memory_dump_config.AddTrigger('light', 1000)
    options.config.chrome_trace_config.SetMemoryDumpConfig(memory_dump_config)

    options.SetTimelineBasedMetrics([
      'expectedQueueingTimeMetric', 'runtimeStatsTotalMetric', 'gcMetric',
      'blinkGcMetric', 'memoryMetric'])
    return options

  @classmethod
  def ValueCanBeAddedPredicate(cls, value, is_first_result):
    # TODO(crbug.com/775942): This is needed because of a race condition in
    # the memory dump manager. Remove this once the bug is fixed.
    if 'memory:unknown_browser' in value.name:
      return ('renderer_processes' in value.name and
              not _IGNORED_MEMORY_STATS_RE.search(value.name))
    # TODO(crbug.com/610962): Remove this stopgap when the perf dashboard
    # is able to cope with the data load generated by TBMv2 metrics.
    if 'memory:chrome' in value.name:
      return ('renderer_processes' in value.name and
              not _IGNORED_MEMORY_STATS_RE.search(value.name))
    if 'v8-gc' in value.name:
      return (_V8_GC_HIGH_LEVEL_STATS_RE.search(value.name) and
              not _IGNORED_V8_STATS_RE.search(value.name))
    # Allow all other metrics.
    return True



@benchmark.Owner(emails=['ulan@chromium.org'])
class V8DesktopBrowsingBenchmark(_V8BrowsingBenchmark):
  PLATFORM = 'desktop'
  SUPPORTED_PLATFORMS = [story.expectations.ALL_DESKTOP]

  def GetExpectations(self):
    class StoryExpectations(story.expectations.StoryExpectations):
      def SetExpectations(self):
        self.DisableStory(
             'browse:news:hackernews',
             [story.expectations.ALL_WIN, story.expectations.ALL_MAC],
             'crbug.com/676336')
        self.DisableStory(
             'browse:news:reddit',
             [story.expectations.ALL_DESKTOP],
             'crbug.com/759777')
        self.DisableStory(
             'browse:news:cnn',
             [story.expectations.ALL_DESKTOP],
             'mac:crbug.com/728576, all:crbug.com/759777')
        self.DisableStory(
             'browse:tools:maps',
             [story.expectations.ALL_MAC],
             'crbug.com/773084')
    return StoryExpectations()

  @classmethod
  def Name(cls):
    return 'v8.browsing_desktop'


@benchmark.Owner(emails=['ulan@chromium.org'])
class V8MobileBrowsingBenchmark(_V8BrowsingBenchmark):
  PLATFORM = 'mobile'
  SUPPORTED_PLATFORMS = [story.expectations.ALL_MOBILE]

  def GetExpectations(self):
    class StoryExpectations(story.expectations.StoryExpectations):
      def SetExpectations(self):
        self.DisableStory(
             'browse:shopping:flipkart',
             [story.expectations.ALL_ANDROID],
             'crbug.com/708300')
        self.DisableStory(
             'browse:news:cnn',
             [story.expectations.ANDROID_NEXUS5X],
             'crbug.com/714650')
        self.DisableStory(
             'browse:news:globo',
             [story.expectations.ALL_ANDROID],
             'crbug.com/714650')
        self.DisableStory(
             'browse:news:toi',
             [story.expectations.ALL_ANDROID],
             'crbug.com/728081')
        # TODO(rnephew): This disabling should move to CanRunOnBrowser.
        self.DisableStory(
             'browse:chrome:omnibox',
             [story.expectations.ANDROID_WEBVIEW],
             'Webview does not have omnibox')
        # TODO(rnephew): This disabling should move to CanRunOnBrowser.
        self.DisableStory(
             'browse:chrome:newtab',
             [story.expectations.ANDROID_WEBVIEW],
             'Webview does not have NTP')
        self.DisableStory(
             'browse:news:cnn',
             [story.expectations.ANDROID_WEBVIEW],
             'Crash: crbug.com/767595')
        self.DisableStory(
             'browse:news:toi',
             [story.expectations.ANDROID_NEXUS5X,
              story.expectations.ANDROID_NEXUS6],
             'Crash: crbug.com/770920')
    return StoryExpectations()

  @classmethod
  def Name(cls):
    return 'v8.browsing_mobile'


@benchmark.Owner(emails=['mythria@chromium.org'])
class V8RuntimeStatsDesktopBrowsingBenchmark(
    _V8RuntimeStatsBrowsingBenchmark):
  PLATFORM = 'desktop'
  SUPPORTED_PLATFORMS = [story.expectations.ALL_DESKTOP]

  def GetExpectations(self):
    class StoryExpectations(story.expectations.StoryExpectations):
      def SetExpectations(self):
        self.DisableStory(
             'browse:news:hackernews',
             [story.expectations.ALL_WIN, story.expectations.ALL_MAC],
             'crbug.com/676336')
        self.DisableStory(
             'browse:news:reddit',
             [story.expectations.ALL_DESKTOP],
             'crbug.com/759777')
        self.DisableStory(
             'browse:news:cnn',
             [story.expectations.ALL_DESKTOP],
             'mac:crbug.com/728576, all:crbug.com/759777')
        self.DisableStory(
             'browse:tools:maps',
             [story.expectations.ALL_MAC],
             'crbug.com/773084')
    return StoryExpectations()

  def SetExtraBrowserOptions(self, options):
    options.AppendExtraBrowserArgs(
      '--enable-blink-features=BlinkRuntimeCallStats')

  @classmethod
  def Name(cls):
    return 'v8.runtimestats.browsing_desktop'


@benchmark.Owner(emails=['mythria@chromium.org'])
class V8RuntimeStatsMobileBrowsingBenchmark(
    _V8RuntimeStatsBrowsingBenchmark):
  PLATFORM = 'mobile'
  SUPPORTED_PLATFORMS = [story.expectations.ALL_MOBILE]

  def SetExtraBrowserOptions(self, options):
    options.AppendExtraBrowserArgs(
      '--enable-blink-features=BlinkRuntimeCallStats')

  def GetExpectations(self):
    class StoryExpectations(story.expectations.StoryExpectations):
      def SetExpectations(self):
        self.DisableStory(
            'browse:shopping:avito',
            [story.expectations.ANDROID_ONE],
            'crbug.com/767970')
        self.DisableStory(
            'browse:news:cnn',
            [story.expectations.ANDROID_ONE],
            'crbug.com/767970')
        self.DisableStory(
            'browse:tech:discourse_infinite_scroll',
            [story.expectations.ANDROID_ONE],
            'crbug.com/767970')
        self.DisableStory(
            'browse:shopping:lazada',
            [story.expectations.ANDROID_ONE],
            'crbug.com/768472')
        self.DisableStory(
            'browse:shopping:flipkart',
            [story.expectations.ALL_MOBILE],
            'crbug.com/767970, crbug.com/708300')
        self.DisableStory(
            'browse:news:cnn',
            [story.expectations.ALL_MOBILE],
            'crbug.com/767970')
        self.DisableStory(
             'browse:news:globo',
             [story.expectations.ALL_ANDROID],
             'crbug.com/714650')
        self.DisableStory(
             'browse:news:toi',
             [story.expectations.ALL_ANDROID],
             'crbug.com/728081')
        # TODO(rnephew): This disabling should move to CanRunOnBrowser.
        self.DisableStory(
             'browse:chrome:omnibox',
             [story.expectations.ANDROID_WEBVIEW],
             'Webview does not have omnibox')
        # TODO(rnephew): This disabling should move to CanRunOnBrowser.
        self.DisableStory(
             'browse:chrome:newtab',
             [story.expectations.ANDROID_WEBVIEW],
             'Webview does not have NTP')
    return StoryExpectations()

  @classmethod
  def Name(cls):
    return 'v8.runtimestats.browsing_mobile'
