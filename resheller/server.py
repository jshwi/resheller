#!/usr/bin/env python3
__author__ = "Stephen Whitlock"
__copyright__ = "Copyright 2019, Jshwi Solutions"
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Stephen Whitlock"
__email__ = "stephen@jshwisolutions.com"
__status__ = "Production"
from src.server.main import main
import sys


sys.path.append('resheller/src')


if __name__ == '__main__':
    main()
