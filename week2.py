from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller
import json

def phase_oracle(qc, qr):
    """
    Build the oracle U_w
    qc: Quantum Circuit object
    qr: Quantum Register object
    """
    # Marks the state '10' as the winner
    qc.z(qr[1])
    qc.cz(qr[0], qr[1])
    
def inversion_about_mean(qc, qr):
    """
    Apply the inversion about mean step
    """
    qc.h(qr)
    qc.x(qr)
    qc.h(qr[1])
    qc.cx(qr[0], qr[1])
    qc.h(qr[1])
    qc.x(qr)
    qc.h(qr)
	
def phase_oracle_anc(qc, qr):
    """
    Oracle with ancilla in qr[2]
    """
	# Similar to phase_oracle, 
	# use a Z-gate on qr[1] to mark '10' as the winner
    qc.z(qr[1])
    qc.h(qr[2])
    qc.ccx(qr[0], qr[1], qr[2])
    qc.h(qr[2])


##### Grover's algorithm without using ancilla bit #####
q = QuantumRegister(2)
c = ClassicalRegister(2)
grover = QuantumCircuit(q, c)

grover.h(q)
phase_oracle(grover, q)
inversion_about_mean(grover, q)
grover.measure(q, c)

backend = Aer.get_backend('qasm_simulator')
job = execute(grover, backend, shots=1024)
counts = job.result().get_counts()

# Find the quantum state with highest probability
max_ = 0
for key in counts:
	if counts[key] > max_:
		max_ = counts[key]
		max_key = key
		
# Calculate the cost of grover without ancilla
pass_ = Unroller(['u3', 'cx'])
pm = PassManager(pass_)
ops = pm.run(grover).count_ops()
cost = ops['u3'] + 10*ops['cx']

print("Results of grover's algorithm without ancilla bit:")
print('\tCounts:', counts)
print('\tQuantum state with highest probability: |%s>' % max_key)
print('\tOperations:', ops)
print('\tCost of grover without ancilla:', cost)

##### Grover's algorithm using ancilla bit #####
q_anc = QuantumRegister(3)
c_anc = ClassicalRegister(3)
grover_anc = QuantumCircuit(q_anc, c_anc)

grover_anc.h(q_anc[0:2])
grover_anc.x(q_anc[2])
phase_oracle_anc(grover_anc, q_anc)
inversion_about_mean(grover_anc, q_anc)
grover_anc.measure(q_anc, c_anc)

job_anc = execute(grover_anc, backend, shots=1024)
counts_anc = job_anc.result().get_counts()

max_ = 0
for key in counts_anc:
	if counts_anc[key] > max_:
		max_ = counts_anc[key]
		max_key = key

# Calculate the cost of grover with ancilla
pass_ = Unroller(['u3', 'cx'])
pm = PassManager(pass_)
ops = pm.run(grover_anc).count_ops()
cost = ops['u3'] + 10*ops['cx']

print("\nResults of grover's algorithm with ancilla bit:")
print('\tCounts:', counts_anc)
print('\tQuantum state with highest probability: |%s>' % max_key)
print('\tOperations:', ops)
print('\tCost of grover with ancilla:', cost)

# Write the results into file
with open('week2_output.txt', 'w') as f:
	f.write(max_key)
	f.write('\n')
	f.write(json.dumps(ops))