#!/usr/bin/env python3
__author__ = "Stephen Whitlock"
__copyright__ = "Copyright 2019, Jshwi Solutions"
__license__ = "MIT"
__version__ = "2019.09"
__maintainer__ = "Stephen Whitlock"
__email__ = "stephen@jshwisolutions.com"
__status__ = "Production"
from src.main import main


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
    except EOFError:
        exit(0)
