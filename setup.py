#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import subprocess


def make_version():
    """Generates a version number using `git describe`.

    Returns:
      version number of the form "3.1.1.dev127+g413ed61".
    """
    def _minimal_ext_cmd(cmd):
        """Run a command in a subprocess.

        Args:
          cmd: list of the command

        Returns:
          output from the command
        """
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            value = os.environ.get(k)
            if value is not None:
                env[k] = value
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               env=env).communicate()[0]
        return out

    version = 'unknown'

    if os.path.exists('.git'):
        try:
            out = _minimal_ext_cmd(['git',
                                    'describe',
                                    '--tags',
                                    '--match',
                                    'v*'])
            # ticket:475 - fix for bytecode received in Py3k
            # http://jeetworks.org/node/67
            out = out.decode("utf-8")
            # convert git long-form version string, e.g.,
            # "version-3_1_1-127-g413ed61", into PEP 440 version,
            # e.g., "3.1.1.dev127+g413ed61"
            version = out.strip().split("-")
            if len(version) > 1:
                version, dev, sha = version
                version = "%s.dev%s+%s" % (version[1:], dev, sha)
            else:
                version = version[0][1:]
        except OSError:
            import warnings
            warnings.warn("Could not run ``git describe``")
    elif os.path.exists('rrc.egg-info'):
        from rrc import get_version
        version = get_version()

    return version

setup(
    name='rrc',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    maintainer='Faical Yannick P. Congo, Daniel Wheeler',
    author_email='yannick.congo@gmail.com',
    description=('The RRC blockchain node.'),
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Programming Language :: Python",
    ],
    entry_points={
        'console_scripts': [
            'rrc = rrc.main.cli:cmd',
        ],
    },
    test_suite='nose.collector',
    tests_require=['nose'],
)
