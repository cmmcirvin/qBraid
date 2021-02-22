from typing import Any, Sequence, Dict, Iterable, Union

from qubit import Qubit

from braket.circuits.qubit_set import QubitSet as BraketQubitSet
from qiskit.circuit.quantumregister import QuantumRegister as QiskitQuantumRegister
from cirq.ops.qubit_order import QubitOrder as CirqQubitOrder


QubitSetInput = Union["BraketQubitSet", "CirqQubitOrder","QiskitQuantumRegister", Iterable[Qubit], Iterable[str], Iterable[int]]  
QubitGetterInput = Union[QubitSetInput,int,str,Iterable]
QubitInput = Union["BraketQubit", "CirqNamedQubit","QiskitQubit", int, str]  


class QubitSet():
    
    """
    A holder instance of QubitSet
    
    Arguments:
        A definitive instance of QubitSet is made from passing an iterable
        of the int or str names to define the qubits. 
        In this case self._qubitset is the identity.
        
    Attributes:
        qubits (list[Qubit]): list of qBraid Qubit objects
        outputs (dict): output objects generated for any or all other packages
        get_qubits(list[QubitInput]): 
    Methods:

    """
    
    def __init__(self, qubits: QubitSetInput = None):
        
        self.qubits = [Qubit(qubit) for qubit in qubits]

    def __len__(self):
        return len(self.qubits)

    def get_qubit_by_id(self, indentifier: Union[str,int]):
        
        for qubit in self.qubits:
            if qubit.id == identifier:
                return qubit
        return "Could not find qubit with id: {}".format(identifier)
    
    def get_qubits(self, targetqubits: Iterable):
        
        """
        search for the qBraid Qubit object in the QubitSet that corresponds to
        each qubit object in the input list
        """
        
        return [self.get_qubit(qubit) for qubit in targetqubits]
    
    def get_qubit(self, targetqubit: QubitInput):
        
        """
        search for the qBraid Qubit object in the QubitSet that corresponds to
        to the passed qubit
        """
        
        for qbraid_qubit in self.qubits:
            if qbraid_qubit.qubit == targetqubit:
                assert type(qbraid_qubit) == Qubit
                return qbraid_qubit
            
    def output(self, output_type: str):
        
        outputs = ['qiskit','cirq','braket']
        if output_type not in outputs:
            print("Cannot output to {}. Possible types include {}".format(output_type,outputs))
        
        if output_type == 'qiskit':
            
            for index, qubit in enumerate(self.qubits):
                qubit.outputs['qiskit'] = index
                
            return self.to_qiskit()
                
    def to_qiskit(self):
        return QiskitQuantumRegister(len(self.qubits))
            
        
            
        
        
    