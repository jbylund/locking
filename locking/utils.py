import sys


def get_caller():
    gpframe = sys._getframe().f_back.f_back
    return f"{gpframe.f_code.co_filename}:{gpframe.f_lineno}"
