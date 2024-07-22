import os


def is_mac():
    return os.uname().sysname == 'Darwin'

def is_linux():
    return os.uname().sysname == 'Linux'

def is_windows():
    return os.uname().sysname == 'Windows'
