# Copyright 2012 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Presubmit script for changes affecting tools/perf/.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts
for more details about the presubmit API built into depot_tools.
"""

import os


def _CommonChecks(input_api, output_api):
  """Performs common checks, which includes running pylint."""
  results = []

  _UpdatePerfData(input_api)
  results.extend(_CheckNoUncommittedFiles(input_api, output_api))

  results.extend(_CheckWprShaFiles(input_api, output_api))
  results.extend(_CheckJson(input_api, output_api))
  results.extend(_CheckExpectations(input_api, output_api))
  results.extend(input_api.RunTests(input_api.canned_checks.GetPylint(
      input_api, output_api, extra_paths_list=_GetPathsToPrepend(input_api),
      pylintrc='pylintrc')))
  return results


def _GetPathsToPrepend(input_api):
  perf_dir = input_api.PresubmitLocalPath()
  chromium_src_dir = input_api.os_path.join(perf_dir, '..', '..')
  telemetry_dir = input_api.os_path.join(
      chromium_src_dir, 'third_party', 'catapult', 'telemetry')
  experimental_dir = input_api.os_path.join(
      chromium_src_dir, 'third_party', 'catapult', 'experimental')
  tracing_dir = input_api.os_path.join(
      chromium_src_dir, 'third_party', 'catapult', 'tracing')
  py_utils_dir = input_api.os_path.join(
      chromium_src_dir, 'third_party', 'catapult', 'common', 'py_utils')
  android_pylib_dir = input_api.os_path.join(
      chromium_src_dir, 'build', 'android')
  return [
      telemetry_dir,
      input_api.os_path.join(telemetry_dir, 'third_party', 'mock'),
      experimental_dir,
      tracing_dir,
      py_utils_dir,
      android_pylib_dir,
  ]


def _RunArgs(args, input_api):
  p = input_api.subprocess.Popen(args, stdout=input_api.subprocess.PIPE,
                                 stderr=input_api.subprocess.STDOUT)
  out, _ = p.communicate()
  return (out, p.returncode)


def _CheckExpectations(input_api, output_api):
  results = []
  perf_dir = input_api.PresubmitLocalPath()
  out, return_code = _RunArgs([
      input_api.python_executable,
      input_api.os_path.join(perf_dir, 'validate_story_expectation_data')],
      input_api)
  if return_code:
    results.append(output_api.PresubmitError(
        'Validating story expectation data failed.', long_text=out))
  return results


def _UpdatePerfData(input_api):
  perf_dir = input_api.PresubmitLocalPath()
  _RunArgs([
      input_api.python_executable,
      input_api.os_path.join(perf_dir, 'generate_perf_data')], input_api)


def _CheckWprShaFiles(input_api, output_api):
  """Check whether the wpr sha files have matching URLs."""
  perf_dir = input_api.PresubmitLocalPath()

  results = []
  wpr_archive_shas = []
  for affected_file in input_api.AffectedFiles(include_deletes=False):
    filename = affected_file.AbsoluteLocalPath()
    if not filename.endswith('.sha1'):
      continue
    wpr_archive_shas.append(filename)

  out, return_code = _RunArgs([
      input_api.python_executable,
      input_api.os_path.join(perf_dir, 'validate_wpr_archives')] +
      wpr_archive_shas,
      input_api)
  if return_code:
    results.append(output_api.PresubmitError(
        'Validating WPR archives failed:', long_text=out))
  return results


def _CheckJson(input_api, output_api):
  """Checks whether JSON files in this change can be parsed."""
  for affected_file in input_api.AffectedFiles(include_deletes=False):
    filename = affected_file.AbsoluteLocalPath()
    if os.path.splitext(filename)[1] != '.json':
      continue
    try:
      input_api.json.load(open(filename))
    except ValueError:
      return [output_api.PresubmitError('Error parsing JSON in %s!' % filename)]
  return []


def _CheckNoUncommittedFiles(input_api, output_api):
  """Ensures that uncommitted updated files will block presubmit."""
  results = []
  diff_text = _RunArgs(['git', 'diff', '--name-only'], input_api)[0]

  if diff_text != "":
    results.append(output_api.PresubmitError(
        ('Please add the following changed files to your git client: %s' %
             diff_text)))
  return results


def CheckChangeOnUpload(input_api, output_api):
  report = []
  report.extend(_CommonChecks(input_api, output_api))
  return report


def CheckChangeOnCommit(input_api, output_api):
  report = []
  report.extend(_CommonChecks(input_api, output_api))
  return report
