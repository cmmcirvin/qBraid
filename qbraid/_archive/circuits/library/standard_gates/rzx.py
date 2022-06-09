from typing import Optional

from ...gate import Gate


class RZX(Gate):
    """2 qubit rotation gate about the x-z plane
    with theta parameter

    Args:
        Gate (ABC): Extends basic gate class
    """

    def __init__(self, theta: float, global_phase: Optional[float] = 0.0):
        super().__init__("RZX", num_qubits=2, params=[theta], global_phase=global_phase)