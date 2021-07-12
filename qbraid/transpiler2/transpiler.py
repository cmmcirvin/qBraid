from .utils import get_package_name
from .wrappers import circuit_wrappers
from qbraid.exceptions import PackageError


def qbraid_wrapper(circuit):

    """Apply qbraid wrapper to a circuit-type object from a supported packasge.
    currently only works for "circuit" objects, but should probably also work
    for gates, instructions, etc."""

    package = get_package_name(circuit)

    if package in circuit_wrappers:
        return circuit_wrappers[package](circuit)
    else:
        raise PackageError(package)