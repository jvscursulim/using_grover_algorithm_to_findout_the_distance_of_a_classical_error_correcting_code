from __future__ import annotations

import numpy as np

from qiskit.circuit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit.library import IntegerComparator
from qiskit_aer import Aer


class GroverParityCheckSolver:
    """GroverParityCheckSolver class"""
    
    def __init__(self) -> GroverParityCheckSolver:
        pass
        
    @staticmethod    
    def find_codewords_and_code_distance(parity_check_matrix: np.ndarray,
                                         init_distance: int=3,
                                         shots: int=10000,
                                         shots_cutoff: int=250) -> tuple:
        """A method that must be used to find the codewords and the distance 
        of the error correction code linked with the input parity check matrix.

        Args:
            parity_check_matrix (np.ndarray): A matrix that define the parity check
            scheme of the error correction code.
            init_distance (int, optional): The first code distance to be tested.
            Defaults to 3.
            shots (int, optional): The number of shots used in the simulation.
            Defaults to 10000.
            shots_cutoff (int, optional): A cutoff used to filter the bitstrings
            (that represents the codewords) with probability amplitude amplified
            by the Grover algorithm. Defaults to 250.

        Returns:
            tuple: A list with the codewords and the distance of the code
            defined by the parity check matrix.
        """

        backend = Aer.get_backend("qasm_simulator")
        count_qubits = int(np.ceil(np.log2(parity_check_matrix.shape[1])))
        found_distance = False

        while not found_distance:

            comparator = IntegerComparator(num_state_qubits=count_qubits,
                                           value=init_distance,
                                           geq=False)

            qubits = QuantumRegister(size=parity_check_matrix.shape[1], name="qubits")
            ancilla = QuantumRegister(size=parity_check_matrix.shape[0], name="ancilla")
            comparator_qubits = QuantumRegister(size=comparator.num_qubits, name="comparator")
            bits = ClassicalRegister(size=parity_check_matrix.shape[1], name="bits")
            bits_counts = ClassicalRegister(size=count_qubits, name="bits_count")
            bits_flag = ClassicalRegister(size=1, name="flag_bit")

            qc = QuantumCircuit(qubits,
                                ancilla,
                                comparator_qubits,
                                bits,
                                bits_counts,
                                bits_flag)

            qc.h(qubit=qubits)
            qc.barrier()

            for i in range(parity_check_matrix.shape[0]):
                for j in range(parity_check_matrix.shape[1]):
                    if parity_check_matrix[i][j] == 1:     
                        qc.cx(control_qubit=qubits[j],
                              target_qubit=ancilla[i])
            qc.barrier()

            qc.x(qubit=ancilla)
            qc.h(qubit=ancilla[-1])
            qc.mcx(control_qubits=ancilla[:-1],
                   target_qubit=ancilla[-1])
            qc.h(qubit=ancilla[-1])
            qc.x(qubit=ancilla)

            qc.barrier()

            for i in range(parity_check_matrix.shape[0]):
                for j in range(parity_check_matrix.shape[1]):
                    if parity_check_matrix[i][j] == 1:     
                        qc.cx(control_qubit=qubits[j],
                              target_qubit=ancilla[i])
            qc.barrier()

            qc.h(qubit=qubits)
            qc.x(qubit=qubits)
            qc.h(qubit=qubits[-1])
            qc.mcx(control_qubits=qubits[:-1],
                   target_qubit=qubits[-1])
            qc.h(qubit=qubits[-1])
            qc.x(qubit=qubits)
            qc.h(qubit=qubits)

            qc.barrier()

            for i in range(parity_check_matrix.shape[1]):
                for j in range(count_qubits-1, -1, -1):
                    if j == 0:
                        qc.cx(control_qubit=qubits[i],
                              target_qubit=comparator_qubits[j])
                    else:
                        control_qubits = [qubits[i]]
                        control_qubits.extend([comparator_qubits[k] for k in range(j)])
                        qc.mcx(control_qubits=control_qubits,
                               target_qubit=comparator_qubits[j])

            qc.barrier()

            qc = qc.compose(other=comparator.decompose().decompose(),
                            qubits=comparator_qubits)

            qc.barrier()

            qc.measure(qubit=qubits, cbit=bits)
            qc.measure(qubit=comparator_qubits[:count_qubits], cbit=bits_counts)
            qc.measure(qubit=comparator_qubits[count_qubits], cbit=bits_flag)

            counts = backend.run(qc, shots=shots).result().get_counts()
            codewords = []
            for bitstring in list(counts.keys()):
                if counts[bitstring] > shots_cutoff:
                    aux = bitstring.split(" ")
                    if aux[0] == '1' and aux[-1] != '0'*qubits.size:
                        found_distance = True
                    codewords.append(aux[-1])

            if not found_distance:
                init_distance += 1
            else:
                code_distance = init_distance - 1

        return codewords, code_distance
        