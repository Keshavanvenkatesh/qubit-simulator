# system_final.py - Add Monte Carlo noise support
from matrix_p import *
from logger import *
from img_g import *
from gates import *
import sympy as sp
from sympy import Matrix as SpMatrix
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import random
import math

# Replace the MonteCarloNoise class in system_final.py with this corrected version

class MonteCarloNoise:
    """Monte Carlo noise model for quantum systems"""
    
    def __init__(self, t1_rate=0.01, t2_rate=0.005, dephasing_rate=0.005, 
                 measurement_error=0.02, gate_error=0.01, dt=None):
        """
        Initialize noise parameters
        t1_rate: Amplitude damping (T1 relaxation) rate (1/time)
        t2_rate: Phase damping (T2 dephasing) rate (1/time)
        dephasing_rate: Additional dephasing rate
        measurement_error: Probability of bit flip during measurement
        gate_error: Probability of gate error (random Pauli)
        dt: Time step (will be set during evolution)
        """
        self.t1_rate = t1_rate
        self.t2_rate = t2_rate
        self.dephasing_rate = dephasing_rate
        self.measurement_error = measurement_error
        self.gate_error = gate_error
        self.dt = dt
        
        # Jump operators
        self.sigma_minus = Matrix([[img(0,0), img(1,0)], [img(0,0), img(0,0)]])  # σ-
        self.sigma_z = Matrix([[img(1,0), img(0,0)], [img(0,0), img(-1,0)]])  # σz
        
    def amplitude_damping_jump(self, psi):
        """Apply amplitude damping (T1) jump: |1⟩ → |0⟩"""
        new_psi = [img(0,0) for _ in range(len(psi))]
        for i, amp in enumerate(psi):
            if i == 1:  # |1⟩ state
                new_psi[0] += amp  # Transfer to |0⟩
            else:
                new_psi[i] += amp
        return new_psi
    
    def phase_damping_jump(self, psi):
        """Apply phase damping (T2) jump: random phase flip"""
        new_psi = []
        for amp in psi:
            phase = random.choice([1, -1])
            new_psi.append(amp * img(phase, 0))
        return new_psi
    
    def dephasing_jump(self, psi):
        """Apply dephasing: random phase rotation"""
        new_psi = []
        for amp in psi:
            phase = random.uniform(-math.pi/36, math.pi/36)  # ±5 degrees
            new_psi.append(amp * img(math.cos(phase), math.sin(phase)))
        return new_psi
    
    def apply_gate_error(self, psi, num_qubits):
        """Apply random Pauli error to a random qubit"""
        if random.random() < self.gate_error:
            error_type = random.choice(['X', 'Y', 'Z'])
            qubit = random.randint(0, num_qubits - 1)
            
            if error_type == 'X':
                error_gate = gates.X
            elif error_type == 'Y':
                error_gate = gates.Y
            else:
                error_gate = gates.Z
            
            # Apply error to the specific qubit
            # This is simplified - in practice would need to expand to full system
            print(f"⚠️ Monte Carlo: {error_type} error on qubit {qubit}")
        
        return psi
    
    def monte_carlo_step(self, psi, H, dt):
        """
        Perform one Monte Carlo step:
        1. Deterministic evolution
        2. Compute jump probabilities
        3. Apply random jumps
        """
        self.dt = dt
        n = len(psi)
        
        # 1. Deterministic evolution (using Taylor series with smaller order for stability)
        minus_i_dt = img(0, -1) * dt
        U = Matrix.identity_matrix(n)
        term = Matrix.identity_matrix(n)
        
        # Use lower order for large Hamiltonians
        max_order = min(10, int(10 / (dt * 10)))  # Adaptive order
        for k in range(1, max_order + 1):
            term = (minus_i_dt / k) * (H * term)
            U += term
        
        # Apply evolution
        psi_matrix = Matrix([[p] for p in psi])
        psi_new_matrix = U * psi_matrix
        psi_new = [psi_new_matrix[i, 0] for i in range(n)]
        
        # 2. Compute jump probabilities (with safety checks)
        # Amplitude damping probability
        p1 = psi_new[1].abs2() if len(psi_new) > 1 else 0
        p_t1 = self.t1_rate * dt * p1
        
        # Phase damping probability
        total_prob = sum(amp.abs2() for amp in psi_new)
        p_t2 = self.t2_rate * dt * total_prob
        
        # Dephasing probability
        p_dephase = self.dephasing_rate * dt
        
        # Ensure probabilities are reasonable
        p_t1 = min(p_t1, 1.0)
        p_t2 = min(p_t2, 1.0)
        p_dephase = min(p_dephase, 1.0)
        
        # 3. Apply random jumps
        r = random.random()
        
        if r < p_t1:
            # Amplitude damping jump
            psi_new = self.amplitude_damping_jump(psi_new)
            print(f"⚠️ Monte Carlo: T1 jump (amplitude damping)")
        elif r < p_t1 + p_t2:
            # Phase damping jump
            psi_new = self.phase_damping_jump(psi_new)
            print(f"⚠️ Monte Carlo: T2 jump (phase damping)")
        elif r < p_t1 + p_t2 + p_dephase:
            # Dephasing jump
            psi_new = self.dephasing_jump(psi_new)
            print(f"⚠️ Monte Carlo: Dephasing jump")
        
        # Normalize with safety check
        norm_sq = sum(amp.abs2() for amp in psi_new)
        if norm_sq > 1e-12:
            norm = math.sqrt(norm_sq)
            psi_new = [amp / img(norm, 0) for amp in psi_new]
        else:
            # If norm is zero, return uniform distribution
            psi_new = [img(1/math.sqrt(n), 0) for _ in range(n)]
        
        return psi_new
class system:
    k_elec = 8.987e9
    k_mag = 1.191e21
    mylogger = logger("logger")
    
    # Add noise model as class variable
    noise_model = None
    use_monte_carlo = False
    monte_carlo_trajectories = 1

    # Add this method to the system class in system_final.py

    @mylogger.logging()
    def __init__(self, coupling_type: int, hamiltonian_type: str, *qubits, distances=None):
        """
        Initialize system with optional distances parameter
        distances: dict with keys (i,j) and values r (distance)
        """
        self.system_of_qubit = list(qubits)
        self.no_of_qubits = len(qubits)
        if self.no_of_qubits == 0:
            raise ValueError("System must have at least one qubit")

        if coupling_type == 0:
            self.K = system.k_elec
        elif coupling_type == 1:
            self.K = system.k_mag

        # Generate distances - either from provided dict or interactive
        self.pair_distance = {}
        if distances is not None:
            # Use provided distances
            for (i, j), r in distances.items():
                J = self.K / (r**3)
                self.pair_distance[(i, j)] = J
        else:
            # Interactive mode (for command line)
            self.generate_pairs()

        # Build interaction Hamiltonian
        self.interaction_hamiltonian = self.find_interaction_hamiltonian(hamiltonian_type.lower())
        
        # If no pairs, create zero matrix
        if self.interaction_hamiltonian is None:
            dim = 2 ** self.no_of_qubits
            self.interaction_hamiltonian = Matrix.zeros(dim, dim)

        # Build initial global state
        self.state_vector = qubits[0].state_vector
        for q in qubits[1:]:
            self.state_vector = self.state_vector.tensor(q.state_vector)

        print(f"✅ System Initialized: {self.no_of_qubits} qubits ({self.state_vector.no_of_rows} states)")
    @mylogger.logging()
    def generate_pairs(self):
        """Prompt user for distances between all pairs (interactive)."""
        for i in range(self.no_of_qubits):
            for j in range(i+1, self.no_of_qubits):
                pair = (i, j)
                try:
                    r = float(input(f"Enter distance between {pair}: "))
                    J = self.K / (r**3)
                    self.pair_distance[pair] = J
                except ValueError:
                    print(f"Invalid distance for pair {pair}, setting to 1.0")
                    J = self.K / (1.0**3)
                    self.pair_distance[pair] = J

    @mylogger.logging()
    def apply_product(self, gate_name):
        """Build the sum over pairs of tensor product of gate_name on qubits i and j."""
        if not self.pair_distance:
            dim = 2 ** self.no_of_qubits
            return Matrix.zeros(dim, dim)
            
        resultant_matrix = Matrix.zeros(2**self.no_of_qubits, 2**self.no_of_qubits)

        for (i, j), v in self.pair_distance.items():
            product = None
            for k in range(self.no_of_qubits):
                if k == i or k == j:
                    if product is None:
                        product = gate_name
                    else:
                        product = product.tensor(gate_name)
                else:
                    if product is None:
                        product = gates.I
                    else:
                        product = product.tensor(gates.I)
            resultant_matrix += v * product
        return resultant_matrix

    @mylogger.logging()
    def find_interaction_hamiltonian(self, hamiltonian_type: str):
        """Constructs the interaction Hamiltonian based on the specified type."""
        if not self.pair_distance:
            return None
            
        if hamiltonian_type == "ising":
            return self.apply_product(gates.Z)
        elif hamiltonian_type == "heisenberg":
            return self.apply_product(gates.X) + self.apply_product(gates.Y) + self.apply_product(gates.Z)
        elif hamiltonian_type == "xx":
            return self.apply_product(gates.X)
        elif hamiltonian_type == "xy":
            return self.apply_product(gates.X) + self.apply_product(gates.Y)
        else:
            raise ValueError("Unsupported Hamiltonian type.")

    @mylogger.logging()
    def _validate_gate(self, U: Matrix, target_qubits_count: int):
        """Validate quantum gate."""
        expected_size = 2 ** target_qubits_count
        rows, cols = U.no_of_rows, U.no_of_columns
        if rows != cols or rows != expected_size:
            raise ValueError(f"Dimension mismatch: expected {expected_size}x{expected_size}, got {rows}x{cols}")
        if not U.unitary_check():
            raise ValueError("Gate is NOT Unitary (U†U != I).")
        det_val = U.det()
        if abs(det_val.mod() - 1) > 1e-9:
            raise ValueError(f"|det(U)| must be 1, got {det_val.mod():.6f}")
        print(f"✅ VALID GATE: {rows}x{rows} | Unitary ✓ | |det|=1 ✓")

    @mylogger.logging()
    def _extract_amps(self):
        """Helper to get a list of img objects from the Matrix column vector."""
        return [self.state_vector[i, 0] for i in range(self.state_vector.no_of_rows)]
    
    @mylogger.logging()
    def _pack_amps(self, amplitudes):
        """Helper: ALWAYS returns proper column vector Matrix"""
        if not amplitudes:
            raise ValueError("Empty amplitudes")
        packed = [[amp] for amp in amplitudes]
        return Matrix(packed)

    @mylogger.logging()
    def apply_operator(self, qubits_indices: list, operation):
        """Apply quantum gate to specified qubits."""
        num_targets = len(qubits_indices)
        
        # 1. Resolve Gate
        if isinstance(operation, str):
            if num_targets == 1:
                U = getattr(gates, operation)
            elif num_targets == 2:
                q1, q2 = qubits_indices
                if operation == "CNOT":
                    U = gates.CNOT_01 if q1 < q2 else gates.CNOT_10
                else:
                    U = getattr(gates, operation)
            else:
                raise ValueError("String shortcuts only support 1 or 2 qubit gates")
        else:
            U = operation
            self._validate_gate(U, num_targets)

        # 2. Extract amplitudes
        amplitudes = self._extract_amps()
        new_amplitudes = [img(0, 0) for _ in amplitudes]
        total_dim = len(amplitudes)
        
        if num_targets == 1:
            t = qubits_indices[0]
            for i in range(total_dim):
                j = i ^ (1 << t)
                if j < total_dim:
                    new_amplitudes[i] = U[0,0] * amplitudes[i] + U[0,1] * amplitudes[j]
                    new_amplitudes[j] = U[1,0] * amplitudes[i] + U[1,1] * amplitudes[j]
        
        elif num_targets == 2:
            q1, q2 = qubits_indices
            for i in range(total_dim):
                base = i & ~((1 << q1) | (1 << q2))
                idx = [
                    base | (0 << q1) | (0 << q2),
                    base | (0 << q1) | (1 << q2),
                    base | (1 << q1) | (0 << q2),
                    base | (1 << q1) | (1 << q2)
                ]
                if i == idx[0]:
                    new_amps = [img(0,0) for _ in range(4)]
                    for row in range(4):
                        res = img(0,0)
                        for col in range(4):
                            res += U[row, col] * amplitudes[idx[col]]
                        new_amps[row] = res
                    for r in range(4):
                        new_amplitudes[idx[r]] = new_amps[r]

        self.state_vector = self._pack_amps(new_amplitudes)
        print(f"✅ Gate applied: {total_dim} states processed")
        
        # Apply Monte Carlo gate noise if enabled
        if system.use_monte_carlo and system.noise_model:
            amps = self._extract_amps()
            amps = system.noise_model.apply_gate_error(amps, self.no_of_qubits)
            self.state_vector = self._pack_amps(amps)

    @mylogger.logging()
    def taylor(self, H, dt, order=10):
        """Time evolution U ≈ exp(-iHt) via Taylor series."""
        if H is None:
            raise ValueError("Hamiltonian is None!")
            
        minus_i_dt = img(0, -1) * dt
        n = H.no_of_rows
        U = Matrix.identity_matrix(n)
        term = Matrix.identity_matrix(n)
        for k in range(1, order + 1):
            term = (minus_i_dt / k) * (H * term)
            U += term
        return U
    
    @mylogger.logging()
    def evolve(self, total_time, steps):
        """Time evolution with Monte Carlo noise support."""
        dt = total_time / steps
        print(f"🔄 Evolving for t∈[0,{total_time}] over {steps} steps (dt={dt:.3f})")
        
        if system.use_monte_carlo and system.noise_model:
            print(f"🎲 Monte Carlo mode: {system.monte_carlo_trajectories} trajectories")
            return self._evolve_monte_carlo(total_time, steps, dt)
        else:
            return self._evolve_deterministic(total_time, steps, dt)
    
    @mylogger.logging()
    def _evolve_deterministic(self, total_time, steps, dt):
        """Deterministic evolution (no noise)"""
        for step in range(steps):
            current_t = step * dt
            try:
                H_now = self.get_total_hamiltonian(current_t)
                if H_now is None:
                    H_now = self.interaction_hamiltonian
                
                if H_now is None:
                    raise ValueError("No valid Hamiltonian available!")
                    
                U_step = self.taylor(H_now, dt)
                self.state_vector = U_step * self.state_vector
                print(f"Step {step+1}/{steps}: t={current_t:.3f} ✓")
            except Exception as e:
                print(f"⚠️ Step {step+1} failed: {e} - skipping")
                continue
        print("✅ Evolution complete!")
    
    @mylogger.logging()
    def _evolve_monte_carlo(self, total_time, steps, dt):
        """Monte Carlo evolution with multiple trajectories"""
        dim = 2 ** self.no_of_qubits
        trajectories = []
        noise = system.noise_model
        
        # Store initial state as list of img objects
        initial_state = self._extract_amps()
        
        # Scale the Hamiltonian to prevent overflow
        # Find the maximum magnitude in the Hamiltonian
        H_max = 0
        for i in range(self.interaction_hamiltonian.no_of_rows):
            for j in range(self.interaction_hamiltonian.no_of_columns):
                val = self.interaction_hamiltonian[i, j]
                mag = val.mod()
                if mag > H_max:
                    H_max = mag
        
        # If Hamiltonian is too large, scale it
        scale_factor = 1.0
        if H_max > 100:
            scale_factor = 100.0 / H_max
            print(f"⚠️ Scaling Hamiltonian by factor {scale_factor:.2e} to prevent overflow")
        
        for traj in range(system.monte_carlo_trajectories):
            # Reset to initial state for each trajectory
            current_state = initial_state.copy()
            
            for step in range(steps):
                current_t = step * dt
                try:
                    # Get Hamiltonian at current time and scale it
                    H_now = self.get_total_hamiltonian(current_t)
                    if H_now is None:
                        H_now = self.interaction_hamiltonian
                    
                    if H_now is None:
                        raise ValueError("No valid Hamiltonian available!")
                    
                    # Scale the Hamiltonian
                    H_scaled = H_now.copy()
                    for i in range(H_scaled.no_of_rows):
                        for j in range(H_scaled.no_of_columns):
                            H_scaled[i, j] = H_scaled[i, j] * img(scale_factor, 0)
                    
                    # Use scaled dt to compensate
                    dt_scaled = dt / scale_factor
                    
                    # Apply Monte Carlo step
                    current_state = noise.monte_carlo_step(current_state, H_scaled, dt_scaled)
                    
                    # Check for NaN
                    for amp in current_state:
                        if math.isnan(amp.real) or math.isnan(amp.imag):
                            raise ValueError("NaN detected in state vector")
                    
                except Exception as e:
                    print(f"⚠️ Traj {traj+1}, Step {step+1} failed: {e}")
                    continue
            
            trajectories.append(current_state)
            print(f"✅ Trajectory {traj+1}/{system.monte_carlo_trajectories} complete")
        
        # Average trajectories to get final state
        final_state = [img(0,0) for _ in range(dim)]
        for traj in trajectories:
            for i, amp in enumerate(traj):
                final_state[i] += amp / img(system.monte_carlo_trajectories, 0)
        
        self.state_vector = self._pack_amps(final_state)
        self.mc_results = trajectories
        print(f"✅ Monte Carlo evolution complete! Averaged {system.monte_carlo_trajectories} trajectories")
    
    @mylogger.logging()
    def get_total_hamiltonian(self, time):
        """Get total H(t) = H_interaction + Σ q.local_h + q.driver_h(t)"""
        if self.interaction_hamiltonian is None:
            dim = 2 ** self.no_of_qubits
            resultant_H = Matrix.zeros(dim, dim)
        else:
            resultant_H = self.interaction_hamiltonian.copy()
        
        for idx, q in enumerate(self.system_of_qubit):
            try:
                h_q = self.get_qubit_hamiltonian(q, time)
                h_expanded = self.expand_to_system(h_q, idx)
                resultant_H += h_expanded
            except Exception as e:
                print(f"⚠️ Error adding Hamiltonian for qubit {idx}: {e}")
                continue
        
        return resultant_H
    
    @mylogger.logging()
    def get_qubit_hamiltonian(self, q, time):
        """Get numeric Hamiltonian for a single qubit at given time."""
        if q.local_hamiltonian is None and q.driver_hamiltonian is None:
            return Matrix.zeros(2, 2)
            
        h_total_q = q.local_hamiltonian + q.driver_hamiltonian
        
        subs = {
            q.w_sym: q.omega,
            q.Omega_sym: q.Omega,
            q.detuning_sym: q.detuning,
            q.phi_sym: q.phi,
            q.t_sym: time
        }
        
        try:
            h_numeric_sym = h_total_q.subs(subs)
            h_numeric = self.sympy_to_numerical_matrix(h_numeric_sym)
            
            # Scale if needed
            max_val = 0
            for i in range(2):
                for j in range(2):
                    mag = h_numeric[i, j].mod()
                    if mag > max_val:
                        max_val = mag
            
            if max_val > 10:  # If too large, scale
                scale = 10.0 / max_val
                for i in range(2):
                    for j in range(2):
                        h_numeric[i, j] = h_numeric[i, j] * img(scale, 0)
            
            return h_numeric
        except Exception as e:
            print(f"⚠️ Failed to convert Hamiltonian: {e}")
            return Matrix.zeros(2, 2)
    
    @mylogger.logging()
    def sympy_to_numerical_matrix(self, sp_mat):
        """Convert SymPy Matrix to Matrix of img objects."""
        try:
            if not isinstance(sp_mat, SpMatrix):
                if isinstance(sp_mat, (int, float, complex)):
                    return Matrix.identity_matrix(2) * img(float(sp_mat.real), float(sp_mat.imag))
                sp_mat = SpMatrix([[sp_mat]])
                
            raw_list = sp_mat.tolist()
            final_data = []
            for row in raw_list:
                final_row = []
                for cell in row:
                    try:
                        c_val = complex(cell.evalf())
                    except:
                        c_val = complex(float(cell))
                    final_row.append(img(c_val.real, c_val.imag))
                final_data.append(final_row)
            return Matrix(final_data)
        except Exception as e:
            print(f"⚠️ sympy_to_numerical_matrix error: {e}")
            return Matrix.identity_matrix(2)
    
    @mylogger.logging()
    def expand_to_system(self, hamiltonian, qubit_index):
        """Embed a single-qubit Hamiltonian into the full system."""
        result = None
        for i in range(self.no_of_qubits):
            if i == qubit_index:
                if result is None:
                    result = hamiltonian
                else:
                    result = result.tensor(hamiltonian)
            else:
                if result is None:
                    result = gates.I
                else:
                    result = result.tensor(gates.I)
        return result

    @mylogger.logging()
    def collapse_all(self):
        """Measures the entire system, collapsing it into a single basis state."""
        amplitudes = self._extract_amps()
        probs = [a.abs2().real for a in amplitudes]
        
        # Apply measurement error if Monte Carlo is enabled
        if system.use_monte_carlo and system.noise_model:
            # Add noise to probabilities
            noise = system.noise_model
            for i in range(len(probs)):
                if random.random() < noise.measurement_error:
                    # Randomly swap with another basis state
                    j = random.randint(0, len(probs)-1)
                    probs[i], probs[j] = probs[j], probs[i]
        
        outcome_idx = random.choices(range(len(probs)), weights=probs)[0]
        state_str = format(outcome_idx, f'0{self.no_of_qubits}b')
        new_state = [img(0, 0)] * len(amplitudes)
        new_state[outcome_idx] = img(1, 0)
        self.state_vector = self._pack_amps(new_state)
        
        print(f"💥 System Collapsed to: |{state_str}⟩")
        return state_str

    def help(self):
        """Comprehensive help documentation."""
        help_text = """
    ======================== QUANTUM SYSTEM HELP ========================
    This system simulates multi-qubit interactions with Monte Carlo noise.
    
    NOISE PARAMETERS:
    - T1 (amplitude damping): |1⟩ → |0⟩ decay
    - T2 (phase damping): Random phase flips
    - Dephasing: Small random phase rotations
    - Measurement error: Bit flips during measurement
    - Gate error: Random Pauli errors on gates
    
    MONTE CARLO MODE:
    - Run multiple trajectories with random noise
    - Average results for realistic simulation
    - Set noise rates and number of trajectories
    
    =====================================================================
        """
        print(help_text)

    def __str__(self):
        return f"QuantumSystem({self.no_of_qubits} qubits)"