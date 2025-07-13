from unittest import TestLoader

def load_tests(loader, tests, pattern):
    return TestLoader().discover(start_dir=__path__[0], pattern=pattern)

