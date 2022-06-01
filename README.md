# Using Grover's algorithm to find out the distance and the code words of a classical error correcting code

## Description

...


## Example:

An example of code snippet that solves the modulo 2 equations of the parity check of the [7,4,3] code (Hamming code).

```python
import numpy as np
from grover_algorithm import GroverParityCheckSolver

matrix_H = np.array([[0,0,0,1,1,1,1],[0,1,1,0,0,1,1],[1,0,1,0,1,0,1]])

gpcs = GroverParityCheckSolver(parity_check_matrix = matrix_H)

code = gpcs.get_classical_error_correction_code()

print(code)
```

Quantum circuit to solve the modulo 2 equations of the parity check matrix of the [7,4,3] code (Hamming code).

![image](example_743.png)