#   encoding: utf-8
#   filename: compat.py

import sys


if (3, 0) <= sys.version_info < (3, 9):
    def removesuffix(self, suffix):
        if self.endswith(suffix):
            return self[:-len(suffix)]
        return self
else:
    removesuffix = str.removesuffix
