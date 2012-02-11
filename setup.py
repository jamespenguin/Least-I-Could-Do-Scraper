from distutils.core import setup
import py2exe

py2exe_options = dict(excludes = ["doctest",
                                  "pdb",
                                  "unittest",
                                  "inspect"])
py2exe_options["bundle_files"] = 1

setup(
    options = {'py2exe': py2exe_options},
    console = [
        {
            "script": "licd.py",
        }
    ],
    zipfile = None,
) 