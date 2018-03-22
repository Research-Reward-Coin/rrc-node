import os


def test():
    r"""
    Run all the doctests available.
    """
    path = os.path.split(__file__)[0]
    print ("Path: {0}".format(path))
    nose.main(argv=['-w', path, '--with-doctest'])


def get_version():
    """Get the version of the code from egg_info.

    Returns:
      the package version number
    """
    from pkg_resources import get_distribution, DistributionNotFound

    try:
        version = get_distribution(__name__).version
    except DistributionNotFound:
        version = "unknown, try running `python setup.py egg_info`"

    return version

__version__ = get_version()

_debug = False

__all__ = ['__version__',
           'test']
