from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import IBMQ, execute
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Unroller
import json

# ************** Quantum Circuit START ************** #

# Submission 3
# Cost: 41556
"""
    q[0] ~ q[13]: node 0 ~ 7
    q[14] ~ q[30]: free ancillae
    q[31]: final ancilla
    
"""

q = QuantumRegister(32, 'q')
c = ClassicalRegister(14)
qc = QuantumCircuit(q, c)

anc = 14 # ancilla index starts

# subroutines to simplify actions
def edge_check(node1, node2, q_out):
    """
        Check edges between nodes.
        
        node1: int
        node2: int
        q_out: QuantumRegister object
    """
    qc.cx(q[2*node1], q[2*node2])
    qc.cx(q[2*node1+1], q[2*node2+1])
    qc.x(q[2*node2])
    qc.x(q[2*node2+1])
    qc.x(q_out)
    qc.ccx(q[2*node2], q[2*node2+1], q_out)
    
def edge_check_fixed(node, abcd, q_out):
    """
        Check edges between node and fixed node (A, B, C, D).
        
        node: int
        abcd: 'A', 'B', 'C' or 'D'
        q_out: QuantumRegister object
    """
    assert abcd == 'A' or abcd == 'B' or abcd == 'C' or abcd == 'D'
    
    if abcd == 'A':
        qc.x(q[2*node])
        qc.x(q[2*node+1])
    elif abcd == 'B':
        qc.x(q[2*node])
    elif abcd == 'C':
        qc.x(q[2*node+1])
    
    qc.x(q_out)
    qc.ccx(q[2*node], q[2*node+1], q_out)
        
def inv_edge_check(node1, node2, q_out):
    qc.ccx(q[2*node2], q[2*node2+1], q_out)
    qc.x(q_out)
    qc.x(q[2*node2+1])
    qc.x(q[2*node2])
    qc.cx(q[2*node1+1], q[2*node2+1])
    qc.cx(q[2*node1], q[2*node2])
    
def inv_edge_check_fixed(node, abcd, q_out):
    assert abcd == 'A' or abcd == 'B' or abcd == 'C' or abcd == 'D'

    qc.ccx(q[2*node], q[2*node+1], q_out)
    qc.x(q_out)
    
    if abcd == 'A':
        qc.x(q[2*node])
        qc.x(q[2*node+1])
    elif abcd == 'B':
        qc.x(q[2*node])
    elif abcd == 'C':
        qc.x(q[2*node+1])
    
def fixed_nodes():
    edge_check_fixed(0, 'A', q[anc])
    edge_check_fixed(1, 'B', q[anc+1])
    # (2, 'A'), (2, 'C')
    edge_check_fixed(3, 'A', q[anc+2])
    edge_check_fixed(4, 'B', q[anc+3])
    edge_check_fixed(5, 'D', q[anc+4])
    edge_check_fixed(6, 'D', q[anc+5])
    qc.mct([q[5]]+q[anc:anc+6], q[30], q[anc+6:anc+11]) # q[5] for (2, 'A') and (2, 'C')
    inv_edge_check_fixed(6, 'D', q[anc+5])
    inv_edge_check_fixed(5, 'D', q[anc+4])
    inv_edge_check_fixed(4, 'B', q[anc+3])
    inv_edge_check_fixed(3, 'A', q[anc+2])
    inv_edge_check_fixed(1, 'B', q[anc+1])
    inv_edge_check_fixed(0, 'A', q[anc])
    qc.barrier()

def node_group1():
    # Nodes: (1,4)
    edge_check(1, 4, q[29])
    qc.x(q[2*4])
    qc.x(q[2*4+1])
    qc.cx(q[2*1+1], q[2*4+1])
    qc.cx(q[2*1], q[2*4])
    qc.barrier()

def inv_node_group1():
    qc.cx(q[2*1], q[2*4])
    qc.cx(q[2*1+1], q[2*4+1])
    qc.x(q[2*4+1])
    qc.x(q[2*4])
    inv_edge_check(1, 4, q[29])
    qc.barrier()

def node_group2():
    # Nodes: (5,6), (3,5), (3,4), (2,3), (0,1), (0,2)
    edge_check(5, 6, q[anc])
    edge_check(3, 5, q[anc+1])
    edge_check(3, 4, q[anc+2])
    edge_check(2, 3, q[anc+3])
    edge_check(0, 1, q[anc+4])
    edge_check(0, 2, q[anc+5])
    qc.mct(q[anc:anc+6], q[28], q[anc+6:anc+10])
    inv_edge_check(0, 2, q[anc+5])
    inv_edge_check(0, 1, q[anc+4])
    inv_edge_check(2, 3, q[anc+3])
    inv_edge_check(3, 4, q[anc+2])
    inv_edge_check(3, 5, q[anc+1])
    inv_edge_check(5, 6, q[anc])
    qc.barrier()
    
def node_group3():
    # Nodes: (3,1), (3,0), (2,5), (6,3), (6,2), (4,6)
    edge_check(3, 1, q[anc])
    edge_check(3, 0, q[anc+1])
    edge_check(2, 5, q[anc+2])
    edge_check(6, 3, q[anc+3])
    edge_check(6, 2, q[anc+4])
    edge_check(4, 6, q[anc+5])
    qc.barrier()
    
def inv_node_group3():
    inv_edge_check(4, 6, q[anc+5])
    inv_edge_check(6, 2, q[anc+4])
    inv_edge_check(6, 3, q[anc+3])
    inv_edge_check(2, 5, q[anc+2])
    inv_edge_check(3, 0, q[anc+1])
    inv_edge_check(3, 1, q[anc])
    qc.barrier()
    
# init
qc.h(q[0:14])
qc.x(q[31])
qc.h(q[31])
qc.barrier()

n_iter = 5 # no. of iterations
for i in range(n_iter):
    ### oracle
    # check the edges of the nodes
    fixed_nodes()
    node_group1()
    node_group2()
    node_group3()
    
    # combine the results
    qc.mct(q[anc:anc+6]+q[28:31], q[31], q[anc+6:anc+13])
    qc.barrier()

    # inversion
    inv_node_group3()
    node_group2() # inversion same as itself
    inv_node_group1()
    fixed_nodes() # inversion same as itself

    ### diffusion step
    qc.h(q[0:14])
    qc.x(q[0:14])
    qc.barrier()
    qc.h(q[13])
    qc.mct(q[0:13], q[13], q[anc:anc+11])
    qc.h(q[13])
    qc.barrier()
    qc.x(q[0:14])
    qc.h(q[0:14])
    qc.barrier()

# measure the results
qc.measure(q[0:14], c)

# ************** Quantum Circuit END ************** #