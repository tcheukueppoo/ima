#!/usr/bin/env python
import sys

if __package__ is None and not hasattr(sys, 'frozen'):
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import ima
#import src as ima

if __name__ == '__main__':
    ima.main()
