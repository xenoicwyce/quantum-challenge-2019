from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute
from qiskit.tools.visualization import plot_histogram
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller
from math import pi
import json

q = QuantumRegister(6, 'q')
c = ClassicalRegister(4, 'c')
qc = QuantumCircuit(q, c)
n_iter = 2 #no. of iterations

# initialization
qc.h(q[0:4])
qc.x(q[5])
qc.h(q[5])
qc.barrier()

for i in range(n_iter):
    # oracle which flips the sign of 0111 and 1000
    # Note: CX itself is an XOR gate classically,
    #       even without ancilla bits.
    qc.cx(q[0], q[1])
    qc.cx(q[0], q[2])
    qc.cx(q[0], q[3])
    qc.mct([q[1], q[2], q[3]], q[5], [q[4]])
    qc.cx(q[0], q[3])
    qc.cx(q[0], q[2])
    qc.cx(q[0], q[1])
    qc.barrier()

    # diffusion
    qc.h(q[0:4])
    qc.x(q[0:4])
    qc.barrier()
    qc.h(q[3])
    qc.mct([q[0], q[1], q[2]], q[3], [q[4]]) #CCCX
    qc.h(q[3])
    qc.barrier()
    qc.x(q[0:4])
    qc.h(q[0:4])
    qc.barrier()

qc.measure(q[0:4], c[0:4])

backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=10000)
counts = job.result().get_counts()
print('Counts:', counts)

pass_ = Unroller(['u3', 'cx'])
pm = PassManager(pass_)
ops = pm.run(qc).count_ops()
cost = ops['u3'] + 10*ops['cx']
print('Operations:', ops)
print('Cost:', cost)

# Write the results into txt file
with open('week3_output.txt', 'w') as f:
    states = [k for (k, v) in counts.items() if v > 1000]
    f.write(states[0])
    f.write(',')
    f.write(states[1])
    f.write('\n')
    f.write(json.dumps(ops))