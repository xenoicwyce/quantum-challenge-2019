from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller
import json

q = QuantumRegister(4, 'q')
c = ClassicalRegister(2, 'c')

def full_adder(qc):
	# The circuit for full adder
    qc.ccx(0, 1, 3)
    qc.cx(0, 1)
    qc.ccx(1, 2, 3)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.measure([2, 3], [0, 1])

for i in range(8):
    # Simulate the circuit for all inputs
    qc = QuantumCircuit(q, c)

    input_ = bin(i)[2:]
    for i in range(len(input_)):
        if input_[i] == '1':
            qc.x(i)
            
    full_adder(qc)

    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1024)
    counts = job.result().get_counts()
    print('Input: %s\tOutput: %s' % (input_, counts))

# Calculate the cost of full adder circuit
qc = QuantumCircuit(q, c)
full_adder(qc)
pass_ = Unroller(['u3', 'cx'])
pm = PassManager(pass_)
ops = pm.run(qc).count_ops()
cost = ops['u3'] + 10*ops['cx']
print('\n%s' % ops)
print('Cost of full adder circuit:', cost)

with open('week1_output.txt', 'w') as f:
	f.write(json.dumps(ops))