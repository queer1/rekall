# Rekall Memory Forensics
# Copyright (C) 2012 Michael Cohen
# Copyright 2013 Google Inc. All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

"""This module provides the base classes for Rekall Renderers.

Renderers are the presentation layer and each one is responsible for
converting the output of the data layer into a specific format, such as
HTML, JSON or text table.
"""


class BaseRenderer(object):
    """All renderers inherit from this."""

    def __init__(self, session=None, fd=None):
        self.session = session
        self.fd = fd
        self.isatty = False
