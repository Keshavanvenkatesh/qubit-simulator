# ⚛️ Quantum Simulator

A **from-scratch quantum computing simulator** built entirely in pure Python — no Qiskit, no Cirq, no NumPy in the core physics engine. Every layer, from complex-number arithmetic to Hamiltonian-driven time evolution, is implemented by hand so that the physics behind every quantum gate stays fully visible and traceable.

Built by a first-year team at VIT Chennai as part of our BAPHY106 coursework.

---

## 📖 What This Project Solves

Most quantum computing frameworks hand you a gate as a ready-made matrix and abstract away *why* it works — how a Hamiltonian becomes a gate, how a control pulse produces a rotation, how measurement collapses a superposition. This simulator was built to answer that question directly: every operation can be traced back to an equation we implemented ourselves, rather than an imported library function.

It lets you:
- Create and inspect single- and multi-qubit states
- Apply standard quantum gates and watch the state vector change
- Evolve a qubit system under a real, physically-defined Hamiltonian (not just a fixed matrix)
- Measure qubits using the Born rule with true probabilistic collapse
- Simulate decoherence (T1/T2 noise) via a Monte Carlo model
- Do all of this through a beginner-friendly GUI, with an AI assistant built in for conceptual help

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Install dependencies
The core physics engine (complex numbers, matrices, gates) has **zero external dependencies** — everything else it needs is in the Python standard library. A few supporting modules do rely on a handful of third-party packages, listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```
> `tkinter` is required for the GUI and ships with most standard Python installations. On Linux, install it separately if missing: `sudo apt-get install python3-tk`

### 3. Run the simulator (GUI)
```bash
python UI_niteesh.py
```

### 4. Run the test suite
```bash
python test.py
```

---

## 🧩 Project Structure

```
├── img_g.py                    # Custom complex-number class (img)
├── matrix_p.py                 # Custom matrix class — linear algebra, tensor products
├── gates.py                    # Quantum gate library (I, X, Y, Z, H, S, T, CNOT, CZ, SWAP)
├── single_qubitclass_y.py      # Single-qubit state, energy levels, symbolic Hamiltonians
├── system_final.py             # Multi-qubit system, tensor composition, time evolution
├── logger.py                   # Dependency-free logging & call-tracing decorator
├── UI_niteesh.py                # Tkinter GUI — Quantum Simulation Studio
├── quantum_chat.py              # In-app AI assistant chat panel
├── test.py                     # Full physics/unit test suite
├── requirements.txt             # Third-party dependencies
└── Quantum_Computing_Simulator_Theory_Report.pdf   # Full theory report
```

---

## 🔬 Core Concepts Implemented

| Concept | Description |
|---|---|
| **Complex numbers** | Full arithmetic (add, subtract, multiply, divide, power, conjugate, modulus, phase) without Python's built-in `complex` type |
| **Matrices & tensor products** | Custom linear algebra engine supporting Kronecker products for multi-qubit Hilbert spaces |
| **Gate library** | I, X, Y, Z, H, S, T (single-qubit); CNOT, CZ, SWAP (two-qubit) |
| **Time evolution** | Closed-form solution for time-independent Hamiltonians + discretized time-ordered exponential (Dyson series) for time-dependent control pulses |
| **Measurement** | Born-rule probability computation with weighted random collapse |
| **Decoherence** | Monte Carlo quantum-trajectory model for T1 relaxation, dephasing, and gate error |

---

## 🖼️ Graphical User Interface
<img width="1600" height="848" alt="WhatsApp Image 2026-07-05 at 1 37 05 PM" src="https://github.com/user-attachments/assets/adf080e4-b57c-4989-8cf2-2171ce18cd52" />
<img width="1600" height="850" alt="WhatsApp Image 2026-07-05 at 1 37 05 PM (1)" src="https://github.com/user-attachments/assets/92eade82-f0eb-4167-9517-74bc91804cfd" />

<img width="1600" height="848" alt="WhatsApp Image 2026-07-05 at 1 37 06 PM" src="https://github.com/user-attachments/assets/ab450606-17fe-46e5-9aa8-5ff86751d339" />

<img width="1600" height="845" alt="WhatsApp Image 2026-07-05 at 1 37 06 PM (1)" src="https://github.com/user-attachments/assets/1d3d2fd1-e5d6-436f-8608-5676e8de8790" />

<img width="1600" height="693" alt="WhatsApp Image 2026-07-05 at 1 37 07 PM" src="https://github.com/user-attachments/assets/f2790db2-609a-4e38-99b7-0c7ed4f19802" />


---

## 📊 Comparison with Existing Frameworks

| Aspect | Qiskit / Mainstream SDKs | This Project |
|---|---|---|
| Gate representation | Fixed, instantaneous matrix | Matrix + explicit Hamiltonian derivation |
| Time evolution | Abstracted away | Modelled explicitly via Schrödinger equation |
| Dependencies | Large SDK | Core engine has none |
| Target audience | Research, production | Learners building intuition |
| Transparency | Internal mechanics hidden | Every operation traceable to first principles |

---

## 📄 Full Report

The complete theoretical background — the physics, the math, and the design rationale behind every module — is available in [`Quantum_Computing_Simulator_Theory_Report.pdf`](./Quantum_Computing_Simulator_Theory_Report.pdf).

---

## 📚 References

1. Griffiths, D. J., *Introduction to Quantum Mechanics*
2. Nielsen, M. A. and Chuang, I. L., *Quantum Computation and Quantum Information*
3. Sakurai, J. J., *Modern Quantum Mechanics*
4. IBM Qiskit Documentation
