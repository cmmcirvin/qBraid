# Copyright 2023 qBraid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit tests for the qbraid device layer.

"""
import cirq
import numpy as np
import pytest
from braket.aws import AwsDevice
from braket.circuits import Circuit as BraketCircuit
from braket.tasks.quantum_task import QuantumTask as AwsQuantumTask
from qiskit import QuantumCircuit as QiskitCircuit
from qiskit_ibm_provider import IBMBackend, IBMJob

from qbraid import QbraidError, device_wrapper, job_wrapper
from qbraid.api import QbraidSession
from qbraid.devices import DeviceError
from qbraid.devices.aws import AwsDeviceWrapper, AwsQuantumTaskWrapper
from qbraid.devices.enums import is_status_final
from qbraid.devices.exceptions import JobStateError
from qbraid.devices.ibm import IBMBackendWrapper, IBMJobWrapper, ibm_least_busy_qpu
from qbraid.interface import random_circuit


def device_wrapper_inputs(vendor: str):
    """Returns list of tuples containing all device_wrapper inputs for given vendor."""
    session = QbraidSession()
    devices = session.get("/public/lab/get-devices", params={}).json()
    input_list = []
    for document in devices:
        if document["vendor"] == vendor:
            input_list.append(document["qbraid_id"])
    return input_list


"""
Device wrapper tests: initialization
Coverage: all vendors, all available devices
"""

inputs_braket_dw = device_wrapper_inputs("AWS")
inputs_qiskit_dw = device_wrapper_inputs("IBM")


def test_job_wrapper_type():
    """Test that job wrapper creates object of original job type"""
    device = device_wrapper("aws_dm_sim")
    circuit = random_circuit("qiskit")
    job_0 = device.run(circuit, shots=10)
    job_1 = job_wrapper(job_0.id)
    assert type(job_0) == type(job_1)
    assert job_0.vendor_job_id == job_1.metadata()["vendorJobId"]


def test_job_wrapper_id_error():
    """Test raising job wrapper error due to invalid job ID."""
    with pytest.raises(QbraidError):
        job_wrapper("Id123")


def test_device_wrapper_id_error():
    """Test raising device wrapper error due to invalid device ID."""
    with pytest.raises(QbraidError):
        device_wrapper("Id123")


@pytest.mark.parametrize("device_id", inputs_braket_dw)
def test_init_braket_device_wrapper(device_id):
    """Test device wrapper for ids of devices available through Amazon Braket."""
    qbraid_device = device_wrapper(device_id)
    vendor_device = qbraid_device.vendor_dlo
    assert isinstance(qbraid_device, AwsDeviceWrapper)
    assert isinstance(vendor_device, AwsDevice)


@pytest.mark.parametrize("device_id", inputs_qiskit_dw)
def test_init_qiskit_device_wrapper(device_id):
    """Test device wrapper for ids of devices available through Qiskit."""
    qbraid_device = device_wrapper(device_id)
    vendor_device = qbraid_device.vendor_dlo
    assert isinstance(qbraid_device, IBMBackendWrapper)
    assert isinstance(vendor_device, IBMBackend)


def test_device_wrapper_properties():
    device_id = "aws_oqc_lucy"
    wrapper = device_wrapper(device_id)
    assert wrapper.provider == "OQC"
    assert wrapper.name == "Lucy"
    assert str(wrapper) == "AWS OQC Lucy device wrapper"
    assert repr(wrapper) == "<AwsDeviceWrapper(OQC:'Lucy')>"


def test_wrap_least_busy():
    device_id = ibm_least_busy_qpu()
    qbraid_device = device_wrapper(device_id)
    assert isinstance(qbraid_device, IBMBackendWrapper)


"""
Device wrapper tests: run method
Coverage: all vendors, one device from each provider (calls to QPU's take time)
"""


def braket_circuit():
    """Returns low-depth, one-qubit Braket circuit to be used for testing."""
    circuit = BraketCircuit()
    circuit.h(0)
    circuit.ry(0, np.pi / 2)
    return circuit


def cirq_circuit(meas=True):
    """Returns Low-depth, one-qubit Cirq circuit to be used for testing.
    If ``meas=True``, applies measurement operation to end of circuit."""
    q0 = cirq.GridQubit(0, 0)

    def basic_circuit():
        yield cirq.H(q0)
        yield cirq.Ry(rads=np.pi / 2)(q0)
        if meas:
            yield cirq.measure(q0, key="q0")

    circuit = cirq.Circuit()
    circuit.append(basic_circuit())
    return circuit


def qiskit_circuit(meas=True):
    """Returns Low-depth, one-qubit Qiskit circuit to be used for testing.
    If ``meas=True``, applies measurement operation to end of circuit."""
    circuit = QiskitCircuit(1, 1) if meas else QiskitCircuit(1)
    circuit.h(0)
    circuit.ry(np.pi / 2, 0)
    if meas:
        circuit.measure(0, 0)
    return circuit


circuits_braket_run = [
    braket_circuit(),
    cirq_circuit(False),
    qiskit_circuit(False),
]  # circuits w/out measurement operation

circuits_cirq_run = [cirq_circuit(), qiskit_circuit()]  # circuit w/ measurement operation
circuits_qiskit_run = circuits_cirq_run
inputs_qiskit_run = ["ibm_q_qasm_sim"]
inputs_braket_run = ["aws_sv_sim"]


@pytest.mark.parametrize("circuit", circuits_qiskit_run)
@pytest.mark.parametrize("device_id", inputs_qiskit_run)
def test_run_qiskit_device_wrapper(device_id, circuit):
    """Test run method from wrapped Qiskit backends"""
    qbraid_device = device_wrapper(device_id)
    qbraid_job = qbraid_device.run(circuit, shots=10)
    vendor_job = qbraid_job.vendor_jlo
    assert isinstance(qbraid_job, IBMJobWrapper)
    assert isinstance(vendor_job, IBMJob)


@pytest.mark.parametrize("circuit", circuits_braket_run)
@pytest.mark.parametrize("device_id", inputs_braket_run)
def test_run_braket_device_wrapper(device_id, circuit):
    """Test run method of wrapped Braket devices"""
    qbraid_device = device_wrapper(device_id)
    qbraid_job = qbraid_device.run(circuit, shots=10)
    vendor_job = qbraid_job.vendor_jlo
    assert isinstance(qbraid_job, AwsQuantumTaskWrapper)
    assert isinstance(vendor_job, AwsQuantumTask)


@pytest.mark.parametrize("device_id", ["aws_sv_sim", "ibm_q_sv_sim"])
def test_cancel_completed_error(device_id):
    """Test that cancelling a job that has already reached its
    final state raises an error."""
    import time

    circuit = circuits_cirq_run[0]
    qbraid_device = device_wrapper(device_id)
    qbraid_job = qbraid_device.run(circuit, shots=10)
    status_final = False
    while not status_final:
        time.sleep(2)
        status = qbraid_job.status()
        status_final = is_status_final(status)
    with pytest.raises(JobStateError):
        qbraid_job.cancel()


def test_circuit_too_many_qubits():
    """Test that run method raises exception when input circuit
    num qubits exceeds that of wrapped Qiskit device."""
    two_qubit_circuit = QiskitCircuit(6)
    two_qubit_circuit.h([0, 1])
    two_qubit_circuit.cx(0, 5)
    one_qubit_device = device_wrapper("ibm_q_belem")
    with pytest.raises(DeviceError):
        one_qubit_device.run(two_qubit_circuit)


def test_device_num_qubits():
    """Test device wrapper num qubits method"""
    five_qubit_device = device_wrapper("ibm_q_belem")
    assert five_qubit_device.num_qubits == 5


def test_wait_for_final_state():
    """Test function that returns after job is complete"""
    device = device_wrapper("aws_dm_sim")
    circuit = random_circuit("qiskit")
    job = device.run(circuit, shots=10)
    job.wait_for_final_state()
    status = job.status()
    assert is_status_final(status)


@pytest.mark.parametrize("device_id", ["ibm_q_sv_sim", "aws_sv_sim"])
def test_result_wrapper_measurements(device_id):
    """Test result wrapper measurements method."""
    circuit = random_circuit("qiskit", num_qubits=3, depth=3, measure=True)
    sim = device_wrapper(device_id).run(circuit, shots=10)
    qbraid_result = sim.result()
    counts = qbraid_result.measurement_counts()
    measurements = qbraid_result.measurements()
    assert isinstance(counts, dict)
    assert measurements.shape == (10, 3)


def test_aws_device_available():
    """Test BraketDeviceWrapper avaliable output identical"""
    device = device_wrapper("aws_dm_sim")
    is_available_bool, is_available_time = device.is_available
    assert is_available_bool == device._get_device().is_available
    assert len(is_available_time.split(":")) == 3
