#!/usr/bin/env python

from distutils.core import setup

import time

r = 1
v = time.strftime("%Y%m%d%H%M")

projectname = "ttyio3"

setup(
  name=projectname,
  version=v,
  url="http://repo.zoidtechnologies.com/%s/" % (projectname),
  author="zoid technologies",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  py_modules=[projectname, "areyousure"],
  requires=["colorclass"],
  scripts=["areyousure"],
  license="GPLv2",
  provides=[projectname],
  classifiers=[
    "Programming Language :: Python :: 3.7",
    "Environment :: Console",
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Terminals",
  ],
  long_description = """terminal input and output functions.""",
  command_options = {
    "build_sphinx": {
      "project": projectname,
      "version": v,
      "release": r,
      "source_dir": ( "setup.py", "doc/" )
    }
  }
)
