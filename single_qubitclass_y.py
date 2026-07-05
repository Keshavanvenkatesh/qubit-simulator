from matrix_p import *
from logger import *
from img_g import *
from gates import *
import sympy as sp
from sympy import Matrix as SpMatrix
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import random
import math

class qubit:
    my_logger = logger("single qubit")
    qubits = []
    H_cut = 1.054571817e-34

    @my_logger.logging()
    def __init__(self, E1: float, E2: float, Omega, detuning: float, phi: float,
                 alpha_real: float, alpha_img: float, beta_real: float, beta_img: float,
                 tolarence: float, local: str, driver: str):
        self.tolarence = tolarence
        [a, b] = self.normalize_state(alpha_real, alpha_img, beta_real, beta_img)

        self.E1 = E1
        self.E2 = E2
        self.omega = (self.E1 - self.E2) / qubit.H_cut
        self.Omega = Omega
        self.detuning = detuning
        self.phi = phi

        self.state_vector = Matrix([[a], [b]])

        # Create SymPy symbols for parameters and time
        self.w_sym = sp.Symbol('w')
        self.Omega_sym = sp.Symbol('Omega')
        self.detuning_sym = sp.Symbol('detuning')
        self.phi_sym = sp.Symbol('phi')
        self.t_sym = sp.Symbol('t')

        # Store symbolic Hamiltonians (SymPy matrices)
        self.local_hamiltonian = self.function(local)
        self.driver_hamiltonian = self.function(driver)

        qubit.qubits.append(self)

    @my_logger.logging()
    def normalise(self):
        return (self.state_vector[0, 0].mod())**2 + (self.state_vector[1, 0].mod())**2

    @my_logger.logging()
    def normality_check(self):
        norm = self.normalise()
        return norm <= 1 + self.tolarence and norm >= 1 - self.tolarence

    @my_logger.logging()
    def collapse(self, basis_0=[[1, 0]], basis_1=[[0, 1]]):
        basis_0 = Matrix(basis_0)
        basis_1 = Matrix(basis_1)
        amp0_matrix = basis_0 * self.state_vector
        amp1_matrix = basis_1 * self.state_vector
        amp0 = amp0_matrix.value()
        amp1 = amp1_matrix.value()
        p0 = amp0.abs2()
        p1 = amp1.abs2()
        total = p0 + p1
        if total != 0:
            p0 /= total
            p1 /= total
        outcome = random.choices([0, 1], weights=[p0, p1])[0]
        return outcome

    @my_logger.logging()
    def normalize_state(self, alpha_real, alpha_img, beta_real, beta_img):
        alpha = img(alpha_real, alpha_img)
        beta = img(beta_real, beta_img)
        norm = alpha.mod()**2 + beta.mod()**2
        if norm <= 1 + self.tolarence and norm >= 1 - self.tolarence:
            return [alpha, beta]
        else:
            norm_factor = math.sqrt(norm)
            print(f"Normalisation not satisfied, using normalised α/β: {alpha/norm_factor}, {beta/norm_factor}")
            return [alpha / norm_factor, beta / norm_factor]

    @my_logger.logging()
    def __str__(self):
        alpha = self.state_vector[0, 0]
        beta = self.state_vector[1, 0]
        alpha_str = f"{alpha}" if alpha.img_num[1] == 0 else f"({alpha})"
        beta_str = f"{beta}" if beta.img_num[1] == 0 else f"({beta})"
        return f"{alpha_str}|0⟩ + {beta_str}|1⟩"

    @my_logger.logging()
    def function(self, eqn: str):
        transformations = standard_transformations + (implicit_multiplication_application,)

        # SymPy Pauli matrices (2x2)
        X_mat = sp.Matrix([[0, 1], [1, 0]])
        Y_mat = sp.Matrix([[0, -sp.I], [sp.I, 0]])
        Z_mat = sp.Matrix([[1, 0], [0, -1]])
        I_mat = sp.eye(2)

        mapping = {
            'w': self.w_sym,
            'W': self.Omega_sym,
            'D': self.detuning_sym,
            'phi': self.phi_sym,
            't': self.t_sym,
            'j': sp.I,
            'I': I_mat,
            'X': X_mat,
            'Y': Y_mat,
            'Z': Z_mat,
            'H': Z_mat   # optional; treat H as Z for simplicity
        }

        raw_expr = parse_expr(eqn, transformations=transformations, local_dict=mapping, evaluate=False)
        expr = sp.sympify(raw_expr)
        # expr is now a SymPy matrix (or scalar, but we expect matrix)
        if not isinstance(expr, SpMatrix):
            # If result is scalar, convert to scalar times identity matrix
            expr = expr * I_mat
        return expr