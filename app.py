import json
import numpy as np
from grover_algorithm import GroverParityCheckSolver

# Define below the parity matrix that you want to know the corresponding
# code words and code distance
matrix_H = np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]])

gpcs = GroverParityCheckSolver(parity_check_matrix = matrix_H)

code = gpcs.get_classical_error_correction_code()

code_string = None

for key, _ in code.items():
    
    code_string = key

with open(f"result\code_{code_string}.json", "w") as file:
    
    json.dump(code, file)
    file.close()

print(code)