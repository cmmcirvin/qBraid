# Copyright (C) 2023 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.

"""
Module defining exceptions for errors raised while processing a device.

"""
from qbraid.exceptions import QbraidError


class DeviceError(QbraidError):
    """Base class for errors raised while processing a device."""


class JobError(QbraidError):
    """Base class for errors raised by Jobs."""


class JobStateError(JobError):
    """Class for errors raised due to the state of a quantum job"""
