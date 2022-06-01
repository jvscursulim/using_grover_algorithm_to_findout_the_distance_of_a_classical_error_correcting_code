import numpy as np
from numpy import ndarray
from qiskit.circuit import QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector


class GroverParityCheckSolver:
    """GroverParityCheckSolver class"""
    
    def __init__(self, parity_check_matrix: ndarray) -> None:
        """
        Args:
            parity_check_matrix (ndarray): The input matrix.  

        Raises:
            TypeError: If the input is not a matrix.
        """
        if isinstance(parity_check_matrix, ndarray):
            
            self.parity_check_matrix = parity_check_matrix
            self.qc = None
        else:
            
            raise TypeError("The input is not a matrix!")
        
    def initialize_qubits(self) -> None:
        """Initilizes the qubits and creates the quantum circuit that will be
        used in the next steps.
        """
        qubits = QuantumRegister(size = self.parity_check_matrix.shape[1], name = "qubits")
        ancilla = QuantumRegister(size = self.parity_check_matrix.shape[0], name = "ancilla")
        oracle = QuantumRegister(size = 1, name = "oracle")
        
        qc = QuantumCircuit(qubits, ancilla, oracle)
        
        qc.h(qubits)
        qc.x(oracle)
        qc.h(oracle)
        qc.barrier()
        
        self.qc = qc
        
    def mod2_equations(self) -> None:
        """Creates the gate sequence that represents the equations
        generated by the input parity check matrix.
        """ 
        for i in range(self.parity_check_matrix.shape[0]):
                
            for j in range(self.parity_check_matrix.shape[1]):
                    
                if self.parity_check_matrix[i][j] == 1:
                        
                    self.qc.cx(control_qubit = self.qc.qregs[0][j], target_qubit = self.qc.qregs[1][i])
                
            self.qc.barrier()
        
    def oracle(self) -> None:
        """Creates the specific oracle for this Grover's algorithm that solves
        the equations generated by the input parity check matrix.
        """
        self.qc.x(self.qc.qregs[1])
        self.qc.mct(control_qubits = self.qc.qregs[1], target_qubit = self.qc.qregs[2])
        self.qc.x(self.qc.qregs[1])
        self.qc.barrier()
        
    def amplitude_amplifier(self) -> None:
        """Creates the amplitude amplifier of the Grover's algorithm.
        """
        self.qc.h(self.qc.qregs[0])
        self.qc.x(self.qc.qregs[0])
        self.qc.h(self.qc.qregs[0][self.parity_check_matrix.shape[1] - 1])
        self.qc.mct(control_qubits = self.qc.qregs[0][:self.parity_check_matrix.shape[1] - 1], target_qubit = self.qc.qregs[0][self.parity_check_matrix.shape[1] - 1])
        self.qc.h(self.qc.qregs[0][self.parity_check_matrix.shape[1] - 1])
        self.qc.x(self.qc.qregs[0])
        self.qc.h(self.qc.qregs[0])
        
    def quantum_circuit(self) -> QuantumCircuit:
        """Creates the quantum circuit of the Grover's algorithm that solves
        the equations of the parity check matrix.

        Returns:
            QuantumCircuit: The quantum circuit that solves the problem.
        """
        self.initialize_qubits()
        
        for _ in range(int(np.round(self.parity_check_matrix.shape[1]/(2**self.parity_check_matrix.shape[0])))):
            
            self.mod2_equations()
            self.oracle()
            self.mod2_equations()
            self.amplitude_amplifier()
        
        self.qc.barrier()    
        self.qc.h(self.qc.qregs[2])
        self.qc.x(self.qc.qregs[2])
            
        return self.qc
    
    def get_classical_error_correction_code(self) -> dict:
        """Computes the CECC from the input parity check matrix and returns
        a dictionary with info about the code.

        Returns:
            dict: A dictionary with the code words and the code distance.
        """
        report = {}
        code_words_list = []
        statevector = Statevector(self.quantum_circuit())
        max_prob = max(statevector.probabilities_dict().values())
        
        for key, value in statevector.probabilities_dict().items():
            
            if value == max_prob:
                
                code_words_list.append(key[self.parity_check_matrix.shape[0]+1:])
              
        code_distance = min([code_word.count('1') for code_word in code_words_list if code_word != '0'*self.parity_check_matrix.shape[1]])
        
        code_string = f"[{self.parity_check_matrix.shape[1]},{self.parity_check_matrix.shape[1]-self.parity_check_matrix.shape[0]},{code_distance}]"
        report[code_string] = {"code_distance": code_distance, "code_words": code_words_list}
        
        return report
        