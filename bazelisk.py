#!/usr/bin/env python3
"""
Copyright 2018 Google Inc. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import platform
import os.path
import subprocess
import shutil
import sys
import urllib.request

def decide_which_bazel_version_to_use():
    # Check in this order:
    # - env var "USE_NIGHTLY_BAZEL" or "USE_BAZEL_NIGHTLY" is set -> latest nightly.
    # - env var "USE_CANARY_BAZEL" or "USE_BAZEL_CANARY" is set -> latest rc.
    # - workspace_root/tools/bazel exists -> that version.
    # - workspace_root/.bazelversion exists -> read contents, that version.
    # - workspace_root/WORKSPACE contains a version -> that version. (TODO)
    # - fallback: latest release
    return "latest"

def find_workspace_root():
    pass

def resolve_version_label_to_number(version):
    if version == "latest":
        # HTTP HEAD to https://github.com/bazelbuild/bazel/releases/latest
        # Check where it resolves to: https://github.com/bazelbuild/bazel/releases/tag/0.17.1
        # Parse the version number from there.
        return "0.17.1"
    else:
        return version

def determine_bazel_filename(version):
    machine = platform.machine()
    if machine != "x86_64":
        raise Exception("Unsupported machine architecture '{}'. Bazel currently only supports x86_64.".format(machine))

    operating_system = platform.system().lower()
    if operating_system not in ("linux", "darwin", "windows"):
        raise Exception("Unsupported operating system '{}'. Bazel currently only supports Linux, macOS and Windows.".format(operating_system))

    return "bazel-{}-{}-{}".format(version, operating_system, machine)

def download_bazel_into_directory(version, directory):
    # Download from here:
    # https://releases.bazel.build/0.17.1/release/index.html
    bazel_filename = determine_bazel_filename(version)
    url = "https://releases.bazel.build/{}/release/{}".format(version, bazel_filename)
    destination_path = os.path.join(directory, bazel_filename)
    if not os.path.exists(destination_path):
        print("Downloading {}...".format(url))
        with urllib.request.urlopen(url) as response, open(destination_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    os.chmod(destination_path, 0o755)
    return destination_path

def main(argv=None):
    if argv is None:
        argv = sys.argv
    bazel_version = decide_which_bazel_version_to_use()
    bazel_version = resolve_version_label_to_number(bazel_version)
    bazel_directory = os.path.join(os.path.expanduser("~"), ".bazelisk", "bin")
    os.makedirs(bazel_directory, exist_ok=True)
    bazel_path = download_bazel_into_directory(bazel_version, bazel_directory)
    return subprocess.Popen([bazel_path] + argv[1:], close_fds=True).wait()

if __name__ == "__main__":
    sys.exit(main())
