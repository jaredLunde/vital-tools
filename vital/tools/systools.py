import sys


def compat(min_version):
    ''' @min_version: (#str) minimum version number formatted like |2.7|
            or |2.7.6|
        -> (#bool) |True| if the system version is at least @min_version
    '''
    return sys.version_info >= tuple(map(int, min_version.split('.')))
