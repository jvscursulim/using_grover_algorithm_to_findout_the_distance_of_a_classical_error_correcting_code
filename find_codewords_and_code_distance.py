import json

import numpy as np

from grover_solver import GroverParityCheckSolver

# Define below the parity matrix that you want to know the corresponding
# code words and code distance
matrix_H = np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]])

gpcs = GroverParityCheckSolver()

codewords, distance = gpcs.find_codewords_and_code_distance(parity_check_matrix=matrix_H)
    
code_string = f"[{matrix_H.shape[1]}, {matrix_H.shape[1]-matrix_H.shape[0]}, {distance}]"
dict_code = {"code": code_string, "codewords": codewords}

with open(f"result\code_{code_string}.json", "w") as file:
    
    json.dump(dict_code, file)
    file.close()

print(dict_code)