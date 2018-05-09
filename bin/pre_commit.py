#!/usr/bin/env python

"""
Related `.git/hooks/pre-commit` file should look like this:

    ```
    #!/bin/bash

    echo "Running flake8..."
    CMD=$("$(pwd -P)/bin/pre_commit.py")

    RESULT=$?
    if [ $RESULT -ne 0 ]; then
        echo "Failed $CMD."
        exit 1
    fi
    echo "No flake8 issues found."

    exit 0
    ```
"""

import contextlib
import fnmatch
import os
import shutil
import subprocess
import sys
import tempfile
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


def pattern_match(file_path, patterns_to_ignore):
    for pattern in patterns_to_ignore:
        if '*' in pattern:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        else:
            if file_path.endswith(pattern):
                return True
    else:
        return False


@contextlib.contextmanager
def make_temporary_directory():
    temporary_directory = tempfile.mkdtemp()
    yield temporary_directory
    shutil.rmtree(temporary_directory, ignore_errors=True)


def get_path_to_dot_git():
    path_to_dot_git = subprocess.check_output('git rev-parse --git-dir', shell=True).strip().decode('utf-8')
    if path_to_dot_git == '.git':
        path_to_dot_git = os.path.join(os.getcwd(), path_to_dot_git)
    elif path_to_dot_git == '.':
        path_to_dot_git = os.getcwd()
    return path_to_dot_git


def get_project_base_path():
    return os.path.split(get_path_to_dot_git())[0]


def get_config_path(project_base_path, config_file_name="setup.cfg"):
    return os.path.join(project_base_path, config_file_name)


def staged_files():
    cmd = "git diff --diff-filter=ACMRTUXB --cached HEAD  --name-only | egrep '\.py$'"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = p.communicate()
    return stdout.decode('utf-8').splitlines()


def get_flake8_error(file, config_path):
    cmd = "flake8 --config=%s %s"
    p = subprocess.Popen(["/bin/bash", "-c", cmd % (config_path, file)], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    if p.returncode == 1:
        return stdout.decode('utf-8')


def get_mypy_error(files, config_path):
    cmd = "mypy --incremental --follow-imports=skip --config-file=%s %s"
    p = subprocess.Popen(["/bin/bash", "-c", cmd % (config_path, ' '.join(files))], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    if p.returncode == 1:
        return stdout.decode('utf-8')


def get_patterns_to_ignore(config_path):
    config = ConfigParser()
    config.read([config_path])
    return config.get('flake8', 'exclude').split(',')


def check_errors(flake8_errors, mypy_errors):
    if flake8_errors:
        flake8_errors.insert(0, '-------------')
        flake8_errors.insert(0, 'Flake8 errors')
    if mypy_errors:
        mypy_errors.insert(0, '-----------')
        mypy_errors.insert(0, 'Mypy errors')

    if flake8_errors or mypy_errors:
        sys.exit('\n'.join(flake8_errors) + '\n\n' + '\n'.join(mypy_errors))


def main():
    project_base_path = get_project_base_path()
    flake8_config_path = get_config_path(project_base_path)
    mypy_config_path = get_config_path(project_base_path, config_file_name="mypy.ini")
    patterns_to_ignore = get_patterns_to_ignore(flake8_config_path)
    flake8_errors = []
    mypy_errors = []
    files_for_mypy = []

    with make_temporary_directory() as tempdir:
        for file in staged_files():
            if not pattern_match(file, patterns_to_ignore):
                actual_full_file_path = os.path.join(project_base_path, file)
                file_dir, file_name = os.path.split(file)
                temp_file_dir = os.path.join(tempdir, file_dir)
                if not os.path.exists(temp_file_dir):
                    os.makedirs(temp_file_dir)
                temp_file_path = os.path.join(temp_file_dir, file_name)
                staged_content = subprocess.check_output(['git', 'show', ':{file}'.format(file=file)])

                with open(temp_file_path, 'wb') as f:
                    f.write(staged_content)

                flake8_error = get_flake8_error(temp_file_path, flake8_config_path)
                if flake8_error is not None:
                    flake8_errors.append(flake8_error.replace(temp_file_path, file).strip())

                # Run on only those files that contain typing imports.
                # We are running this on the actual files instead of stages content as
                # otherwise mypy has issues with imported files.
                # TODO: Try to detect annotations in the source code
                if b'import typing' in staged_content or b'from typing import' in staged_content:
                    files_for_mypy.append(actual_full_file_path)

    if files_for_mypy:
        mypy_error = get_mypy_error(files_for_mypy, mypy_config_path)
        if mypy_error is not None:
            mypy_errors.extend(mypy_error.strip().splitlines())
    check_errors(flake8_errors, mypy_errors)


if __name__ == '__main__':
    main()
