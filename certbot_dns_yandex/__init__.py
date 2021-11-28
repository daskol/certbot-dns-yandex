#   encoding: utf8
#   filename: __init__.py

import builtins
import sys

if (3, 0) <= sys.version_info < (3, 9):

    class PatchedBuiltInStr(str):

        def removesuffix(self, suffix, /):
            if self.endswith(suffix):
                return suffix[:-len(suffix)]
            return suffix

    builtins.str = PatchedBuiltInStr
