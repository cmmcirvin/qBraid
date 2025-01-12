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
Unit tests for the qbraid transpiler conversions module.

"""
import cirq
import numpy as np
import pytest

from qbraid._qprogram import QPROGRAM_LIBS
from qbraid.interface import to_unitary
from qbraid.transpiler.conversions import convert_from_cirq


@pytest.mark.parametrize("frontend", QPROGRAM_LIBS)
def test_convert_circuit_operation_from_cirq(frontend):
    q = cirq.NamedQubit("q")
    cirq_circuit = cirq.Circuit(
        cirq.Y(q), cirq.CircuitOperation(cirq.FrozenCircuit(cirq.X(q)), repetitions=5), cirq.Z(q)
    )

    test_circuit = convert_from_cirq(cirq_circuit, frontend)

    cirq_unitary = to_unitary(cirq_circuit)
    test_unitary = to_unitary(test_circuit)

    assert np.allclose(cirq_unitary, test_unitary)
