# -*- coding: utf-8 -*-
#
#  documentation build configuration file, created by
# sphinx-quickstart on Sun Feb 17 11:46:20 2013.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys, os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

sys.path.insert(0, os.path.abspath('../cla_backend/apps/'))
sys.path.insert(0, os.path.abspath('../cla_backend/libs/'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../../cla_docs/docs/source/'))
from common_conf import *

extensions += ['docs.swag']

# -- General configuration -----------------------------------------------------

# General information about the project.
project = u'Civil Legal Aid Backend (API Server)'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# The full version, including alpha/beta/rc tags.

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

