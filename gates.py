# gates.py
from matrix_p import *
from img_g import *
import math

class gates:
    # 1-Qubit Gates (Pauli + Hadamard)
    I = Matrix([[img(1,0), img(0,0)],
                [img(0,0), img(1,0)]])
    
    X = Matrix([[img(0,0), img(1,0)],
                [img(1,0), img(0,0)]])
    
    Y = Matrix([[img(0,0), img(0,-1)],
                [img(0,1), img(0,0)]])
    
    Z = Matrix([[img(1,0), img(0,0)],
                [img(0,0), img(-1,0)]])
    
    # Fixed Hadamard gate - need to ensure proper complex numbers
    H = Matrix([[img(1/math.sqrt(2), 0), img(1/math.sqrt(2), 0)],
                [img(1/math.sqrt(2), 0), img(-1/math.sqrt(2), 0)]])
    
    # 2-Qubit Gates (Controlled operations)
    # CNOT: Control on qubit 0 (first qubit), target on qubit 1 (second qubit)
    CNOT_01 = Matrix([
        [img(1,0), img(0,0), img(0,0), img(0,0)],  # |00⟩ → |00⟩
        [img(0,0), img(1,0), img(0,0), img(0,0)],  # |01⟩ → |01⟩
        [img(0,0), img(0,0), img(0,0), img(1,0)],  # |10⟩ → |11⟩
        [img(0,0), img(0,0), img(1,0), img(0,0)]   # |11⟩ → |10⟩
    ])
    
    # CNOT: Control on qubit 1 (second qubit), target on qubit 0 (first qubit)
    CNOT_10 = Matrix([
        [img(1,0), img(0,0), img(0,0), img(0,0)],  # |00⟩ → |00⟩
        [img(0,0), img(0,0), img(0,0), img(1,0)],  # |01⟩ → |11⟩
        [img(0,0), img(0,0), img(1,0), img(0,0)],  # |10⟩ → |10⟩
        [img(0,0), img(1,0), img(0,0), img(0,0)]   # |11⟩ → |01⟩
    ])
    
    # CZ: Controlled-Z (Phase flip)
    CZ = Matrix([
        [img(1,0), img(0,0), img(0,0), img(0,0)],
        [img(0,0), img(1,0), img(0,0), img(0,0)],
        [img(0,0), img(0,0), img(1,0), img(0,0)],
        [img(0,0), img(0,0), img(0,0), img(-1,0)]
    ])
    
    # SWAP: Swap two qubits
    SWAP = Matrix([
        [img(1,0), img(0,0), img(0,0), img(0,0)],
        [img(0,0), img(0,0), img(1,0), img(0,0)],
        [img(0,0), img(1,0), img(0,0), img(0,0)],
        [img(0,0), img(0,0), img(0,0), img(1,0)]
    ])
    
    # Additional useful gates
    S = Matrix([[img(1,0), img(0,0)],
                [img(0,0), img(0,1)]])  # Phase gate
    
    T = Matrix([[img(1,0), img(0,0)],
                [img(0,0), img(1/math.sqrt(2), 1/math.sqrt(2))]])  # T gate (π/8)
    
    @staticmethod
    def get_cnot(control_qubit, target_qubit, num_qubits=2):
        """Generate CNOT for arbitrary qubit positions"""
        if num_qubits != 2:
            raise ValueError("Only 2-qubit CNOT supported")
        # If control is qubit 0, target is qubit 1, use CNOT_01
        # If control is qubit 1, target is qubit 0, use CNOT_10
        if control_qubit == 0 and target_qubit == 1:
            return gates.CNOT_01
        elif control_qubit == 1 and target_qubit == 0:
            return gates.CNOT_10
        else:
            raise ValueError(f"Invalid control/target for 2-qubit system: c={control_qubit}, t={target_qubit}")
    
    @staticmethod
    def get_gate(name):
        """Get gate by name"""
        gate_dict = {
            'I': gates.I,
            'X': gates.X,
            'Y': gates.Y,
            'Z': gates.Z,
            'H': gates.H,
            'S': gates.S,
            'T': gates.T,
            'CNOT_01': gates.CNOT_01,
            'CNOT_10': gates.CNOT_10,
            'CNOT': gates.CNOT_01,  # Default CNOT with control on qubit 0
            'CZ': gates.CZ,
            'SWAP': gates.SWAP
        }
        return gate_dict.get(name, None)
    
    def __str__(self):
        return "Quantum Gates: I, X, Y, Z, H, S, T, CNOT_01, CNOT_10, CZ, SWAP"

# Make the class available at module level
__all__ = ['gates']