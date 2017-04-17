import os

__version__ = '1.0.1'


def get_path():
    return os.path.abspath(os.path.dirname(__file__))


def setup(app):
    return {
        'version': __version__,
        'parallel_read_safe': True
    }
