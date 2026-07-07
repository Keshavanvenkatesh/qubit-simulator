
import shlex
# quantum_ui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sys
from io import StringIO
import os
import subprocess

# Import your quantum classes
from single_qubitclass_y import qubit
from system_final import *
from matrix_p import Matrix, img
from gates import gates
import math

class QuantumUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Simulation Studio")
        self.root.geometry("1400x800")
        
        # Store qubits and system
        self.qubits = []
        self.current_system = None
        self.qubit_buttons = []
        
        # Configure style
        self.setup_styles()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.create_main_layout()
        
        # Initialize output redirect
        self.setup_output_redirect()
        
        # Welcome message
        self.print_to_console("=== Quantum Simulation Studio ===")
        self.print_to_console("Type Windows-like commands in the prompt below")
        self.print_to_console("Examples: dir, cd .., mkdir test, echo Hello\n")
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12))
        style.configure('Console.TFrame', relief='sunken', borderwidth=2)
        
    def setup_output_redirect(self):
        """Redirect stdout to console widget"""
        self.output_buffer = StringIO()
        self.old_stdout = sys.stdout
        
        class ConsoleRedirect:
            def __init__(self, ui):
                self.ui = ui
                self.buffer = ""
                
            def write(self, text):
                if not text:
                    return

                self.buffer += text
                while "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    self.ui.print_to_console(line, scroll=True)
                    
            def flush(self):
                if self.buffer:
                    self.ui.print_to_console(self.buffer, scroll=True)
                    self.buffer = ""
                
        sys.stdout = ConsoleRedirect(self)
        
    def create_menu_bar(self):
        """Create menu bar at top"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Session", command=self.save_session)
        file_menu.add_command(label="Load Session", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Console", command=self.clear_console)
        edit_menu.add_command(label="Clear All Qubits", command=self.clear_all_qubits)
        
        # View menu
# View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show State Vector", command=self.show_state_vector)
        view_menu.add_command(label="Show Hamiltonian", command=self.show_hamiltonian)
        view_menu.add_command(label="Show MC Results", command=self.show_mc_results)  # Add this
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Monte Carlo", command=self.toggle_monte_carlo)  # Add this
        view_menu.add_separator()
        view_menu.add_command(label="Show ChatGPT", command=self.toggle_chat)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Logs menu
        logs_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Logs", menu=logs_menu)
        logs_menu.add_command(label="View Logs", command=self.show_logs)
        logs_menu.add_command(label="Clear Logs", command=self.clear_logs)
        
    def toggle_chat(self):
        """Toggle chat visibility"""
        if hasattr(self, 'chat_panel'):
            if self.chat_panel.winfo_ismapped():
                self.main_paned.forget(self.chat_panel)
            else:
                self.main_paned.add(self.chat_panel, weight=2)

    def normalize_hamiltonian(self):
        """Normalize the Hamiltonian to prevent numerical overflow"""
        if not self.current_system:
            return
        
        # Get max element magnitude
        H = self.current_system.interaction_hamiltonian
        max_mag = 0
        for i in range(H.no_of_rows):
            for j in range(H.no_of_columns):
                val = H[i, j]
                mag = val.mod()
                if mag > max_mag:
                    max_mag = mag
        
        if max_mag > 100:
            scale = 100.0 / max_mag
            self.print_to_console(f"⚠️ Hamiltonian magnitude is {max_mag:.2e}, scaling by {scale:.2e}", "warning")
            
            # Scale the Hamiltonian
            for i in range(H.no_of_rows):
                for j in range(H.no_of_columns):
                    H[i, j] = H[i, j] * img(scale, 0)
            
            # Also scale the time to compensate
            self.print_to_console(f"   Time will be scaled accordingly during evolution", "info")

    def toggle_monte_carlo(self):
        """Toggle Monte Carlo noise on/off"""
        from system_final import system
        
        if system.use_monte_carlo:
            system.use_monte_carlo = False
            system.noise_model = None
            system.monte_carlo_trajectories = 1
            self.print_to_console("❌ Monte Carlo noise DISABLED", "info")
            if hasattr(self, 'mc_indicator'):
                self.mc_indicator.config(text="", foreground="black")
            self.update_status("Monte Carlo disabled")
        else:
            # Show noise configuration popup
            self.show_noise_popup()
    def create_main_layout(self):
        """Create main UI layout"""
        # Top toolbar
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Toolbar buttons
        buttons = [
            ("LOAD", self.load_session, "Load a saved session"),
            ("NEW QUBIT", self.show_new_qubit_popup, "Create a new qubit"),
            ("BUILD SYSTEM", self.build_system, "Build multi-qubit system"),
            ("CLEAR", self.clear_all_qubits, "Reset qubits, system state, and memory"),
        ]
        
        for text, command, tooltip in buttons:
            btn = ttk.Button(toolbar_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5)
            self.create_tooltip(btn, tooltip)
        
        # Status label
        # Status label
        self.status_label = ttk.Label(toolbar_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Monte Carlo indicator (add this)
        self.mc_indicator = ttk.Label(toolbar_frame, text="", relief=tk.SUNKEN)
        self.mc_indicator.pack(side=tk.RIGHT, padx=5)
        
        # Main content area (left + center)
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Qubit list
        left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(left_frame, weight=1)
        
        # Left panel title
        ttk.Label(left_frame, text="Qubits", style='Title.TLabel').pack(pady=5)
        
        # Qubit list frame (scrollable)
        self.qubit_list_frame = ttk.Frame(left_frame)
        self.qubit_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for qubit list
        qubit_scrollbar = ttk.Scrollbar(self.qubit_list_frame)
        qubit_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.qubit_list = tk.Canvas(self.qubit_list_frame, yscrollcommand=qubit_scrollbar.set)
        self.qubit_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        qubit_scrollbar.config(command=self.qubit_list.yview)
        
        self.qubit_frame = ttk.Frame(self.qubit_list)
        self.qubit_list.create_window((0, 0), window=self.qubit_frame, anchor="nw")
        
        self.qubit_frame.bind("<Configure>", lambda e: self.qubit_list.configure(scrollregion=self.qubit_list.bbox("all")))
        
        # Center panel - Command prompt and output
        center_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(center_frame, weight=3)
        
        # Command input area
        cmd_frame = ttk.Frame(center_frame)
        cmd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(cmd_frame, text="COMMAND PROMPT", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.cmd_entry = ttk.Entry(cmd_frame)
        self.cmd_entry.pack(fill=tk.X, pady=5)
        self.cmd_entry.bind('<Return>', lambda e: self.run_command())
        
        # Output area
        output_frame = ttk.Frame(center_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(output_frame, text="OUTPUT", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.console = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=20, 
                                                   bg='black', fg='white', font=('Courier', 10))
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colors
        self.console.tag_config("error", foreground="red")
        self.console.tag_config("success", foreground="green")
        self.console.tag_config("info", foreground="cyan")
        
        # Quantum Operations Panel
        ops_frame = ttk.LabelFrame(center_frame, text="Quantum Operations", padding=5)
        ops_frame.pack(fill=tk.X, pady=5)

        # Right panel - ChatGPT assistant
        self.chat_panel = ttk.Frame(self.main_paned)
        self.main_paned.add(self.chat_panel, weight=2)

        from quantum_chat import QuantumChat
        self.chat = QuantumChat(self.chat_panel, context_provider=self.get_chat_context)
        self.chat.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Gate application
        gate_frame = ttk.Frame(ops_frame)
        gate_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(gate_frame, text="Apply Gate:").pack(side=tk.LEFT, padx=5)
        self.gate_qubits_entry = ttk.Entry(gate_frame, width=10)
        self.gate_qubits_entry.pack(side=tk.LEFT, padx=5)
        self.gate_qubits_entry.insert(0, "0")
        
        self.gate_combo = ttk.Combobox(gate_frame, values=['H', 'X', 'Y', 'Z', 'I', 'S', 'T', 'CNOT', 'SWAP'], width=8)
        self.gate_combo.pack(side=tk.LEFT, padx=5)
        self.gate_combo.set('H')
        
        ttk.Button(gate_frame, text="Apply", command=self.apply_gate).pack(side=tk.LEFT, padx=5)
        
        # Evolution
        evolve_frame = ttk.Frame(ops_frame)
        evolve_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(evolve_frame, text="Evolve:").pack(side=tk.LEFT, padx=5)
        ttk.Label(evolve_frame, text="Time:").pack(side=tk.LEFT)
        self.evolve_time = ttk.Entry(evolve_frame, width=10)
        self.evolve_time.pack(side=tk.LEFT, padx=5)
        self.evolve_time.insert(0, "1.0")
        
        ttk.Label(evolve_frame, text="Steps:").pack(side=tk.LEFT)
        self.evolve_steps = ttk.Entry(evolve_frame, width=10)
        self.evolve_steps.pack(side=tk.LEFT, padx=5)
        self.evolve_steps.insert(0, "10")
        
        ttk.Button(evolve_frame, text="Run Evolution", command=self.run_evolution).pack(side=tk.LEFT, padx=5)
        
        # Measurement
        measure_frame = ttk.Frame(ops_frame)
        measure_frame.pack(fill=tk.X, pady=2)
        ttk.Button(measure_frame, text="Measure System", command=self.measure_system).pack(side=tk.LEFT, padx=5)
        
        # State and Hamiltonian display
        # State and Hamiltonian display
        info_frame = ttk.Frame(ops_frame)
        info_frame.pack(fill=tk.X, pady=2)
        ttk.Button(info_frame, text="Show State Vector", command=self.show_state_vector).pack(side=tk.LEFT, padx=5)
        ttk.Button(info_frame, text="Show Hamiltonian", command=self.show_hamiltonian).pack(side=tk.LEFT, padx=5)
        # ADD THIS LINE:
        ttk.Button(info_frame, text="MC Results", command=self.show_mc_results).pack(side=tk.LEFT, padx=5)
        
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="yellow", relief="solid")
            label.pack()
            widget.tooltip = tooltip
            
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
        
    def print_to_console(self, text, tag=None, scroll=True):
        """Print text to console with optional color tag"""
        self.console.insert(tk.END, text + "\n", tag)
        if scroll:
            self.console.see(tk.END)
        self.root.update()

    def _format_console_scalar(self, value, precision=4):
        """Format scalar values compactly for aligned console output."""
        if hasattr(value, "real") and hasattr(value, "imag"):
            real = 0.0 if abs(value.real) < 1e-12 else value.real
            imag = 0.0 if abs(value.imag) < 1e-12 else value.imag

            if imag == 0:
                return f"{real:.{precision}g}"
            if real == 0:
                return f"{imag:.{precision}g}i"
            sign = "+" if imag >= 0 else "-"
            return f"{real:.{precision}g} {sign} {abs(imag):.{precision}g}i"
        if isinstance(value, float):
            return f"{value:.{precision}g}"
        return str(value)

    def _format_matrix_for_console(self, matrix, identity="Matrix", basis_labels=False):
        """Return a multi-line string with aligned matrix/state-vector formatting."""
        rows = []
        for i in range(matrix.no_of_rows):
            row = [self._format_console_scalar(matrix[i, j]) for j in range(matrix.no_of_columns)]
            rows.append(row)

        if not rows:
            return f"{identity} = []"

        if basis_labels and matrix.no_of_columns == 1:
            width = max(len(row[0]) for row in rows)
            label_width = max(1, len(format(max(0, matrix.no_of_rows - 1), "b")))
            lines = [f"{identity} ="]
            for idx, row in enumerate(rows):
                basis = format(idx, f"0{label_width}b")
                lines.append(f"  |{basis}> : {row[0].rjust(width)}")
            return "\n".join(lines)

        col_widths = [
            max(len(rows[i][j]) for i in range(len(rows)))
            for j in range(matrix.no_of_columns)
        ]

        lines = [f"{identity} ="]
        for row in rows:
            padded = [row[j].rjust(col_widths[j]) for j in range(len(row))]
            lines.append("  | " + "  ".join(padded) + " |")
        return "\n".join(lines)

    def print_matrix_to_console(self, matrix, identity="Matrix", basis_labels=False, tag="info"):
        """Pretty-print a matrix or state vector into the black console."""
        formatted = self._format_matrix_for_console(matrix, identity=identity, basis_labels=basis_labels)
        for line in formatted.splitlines():
            self.print_to_console(line, tag)
        
    def clear_console(self):
        """Clear console output"""
        self.console.delete(1.0, tk.END)

    def get_chat_context(self):
        """Build a concise summary of the current simulator state for chat context."""
        lines = []
        lines.append(f"Number of created qubits: {len(self.qubits)}")

        if self.qubits:
            for index, q in enumerate(self.qubits, start=1):
                lines.append(
                    f"Qubit {index}: E1={q.E1}, E2={q.E2}, Omega={q.Omega}, "
                    f"detuning={q.detuning}, phi={q.phi}"
                )

        if not self.current_system:
            lines.append("Current system: not built yet")
            return "\n".join(lines)

        system_obj = self.current_system
        lines.append(f"Current system: {system_obj}")
        lines.append(f"System qubits: {system_obj.no_of_qubits}")

        if hasattr(system_obj, "pair_distance") and system_obj.pair_distance:
            pair_parts = []
            for (i, j), coupling in sorted(system_obj.pair_distance.items()):
                pair_parts.append(f"Q{i+1}-Q{j+1}={coupling:.3e}")
            lines.append("Pair couplings: " + ", ".join(pair_parts))
        else:
            lines.append("Pair couplings: none")

        try:
            amplitudes = system_obj._extract_amps()
            basis_terms = []
            max_terms = min(8, len(amplitudes))
            for idx in range(max_terms):
                state = format(idx, f"0{system_obj.no_of_qubits}b")
                basis_terms.append(f"|{state}>={amplitudes[idx]}")
            lines.append("State vector sample: " + ", ".join(basis_terms))
        except Exception as exc:
            lines.append(f"State vector sample unavailable: {exc}")

        try:
            hamiltonian = system_obj.interaction_hamiltonian
            lines.append(
                f"Interaction Hamiltonian size: "
                f"{hamiltonian.no_of_rows}x{hamiltonian.no_of_columns}"
            )
        except Exception as exc:
            lines.append(f"Interaction Hamiltonian unavailable: {exc}")

        from system_final import system
        lines.append(f"Monte Carlo enabled: {system.use_monte_carlo}")
        lines.append(f"Monte Carlo trajectories: {system.monte_carlo_trajectories}")
        if system.noise_model:
            noise = system.noise_model
            lines.append(
                "Noise model: "
                f"T1={noise.t1_rate}, T2={noise.t2_rate}, "
                f"dephasing={noise.dephasing_rate}, measurement={noise.measurement_error}, "
                f"gate={noise.gate_error}"
            )
        else:
            lines.append("Noise model: none")

        if hasattr(system_obj, "mc_results") and system_obj.mc_results:
            lines.append(f"Saved Monte Carlo trajectories: {len(system_obj.mc_results)}")

        return "\n".join(lines)
        
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update()
        
    def run_command(self):
        """Execute shell command"""
        command = self.cmd_entry.get().strip()
        if command:
            self.print_to_console(f"\n> {command}", "info")
            self.execute_shell_command(command)
            self.cmd_entry.delete(0, tk.END)
            
    def execute_shell_command(self, command):
        """Execute a system shell command and display output"""
        try:
            # Use subprocess to run command with shell
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
            stdout, stderr = process.communicate()
            
            if stdout:
                self.print_to_console(stdout.rstrip())
            if stderr:
                self.print_to_console(stderr.rstrip(), "error")
                
        except Exception as e:
            self.print_to_console(f"Error executing command: {e}", "error")
            
    def show_new_qubit_popup(self):
        """Show popup window for creating new qubit"""
        # [Keep the same as before]
        # (Same code as previous version)
        popup = tk.Toplevel(self.root)
        popup.title("Create New Qubit")
        popup.geometry("500x600")
        popup.transient(self.root)
        popup.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(popup)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Basic parameters
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Parameters")
        
        # Create input fields
        fields = {}
        labels = [
            ("E₁:", "E1"),
            ("E₂:", "E2"),
            ("Ω:", "Omega"),
            ("Δ:", "detuning"),
            ("Φ:", "phi"),
            ("α real:", "alpha_real"),
            ("α img:", "alpha_img"),
            ("β real:", "beta_real"),
            ("β img:", "beta_img"),
            ("Tolerance:", "tolarence")
        ]
        
        row = 0
        for label_text, field_name in labels:
            ttk.Label(basic_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(basic_frame, width=30)
            entry.grid(row=row, column=1, padx=5, pady=5)
            fields[field_name] = entry
            row += 1
            
        # Set default values
        fields["E1"].insert(0, "1.0")
        fields["E2"].insert(0, "0.0")
        fields["Omega"].insert(0, "1.0")
        fields["detuning"].insert(0, "0.0")
        fields["phi"].insert(0, "0.0")
        fields["alpha_real"].insert(0, "1.0")
        fields["alpha_img"].insert(0, "0.0")
        fields["beta_real"].insert(0, "0.0")
        fields["beta_img"].insert(0, "0.0")
        fields["tolarence"].insert(0, "1e-9")
        
        # Tab 2: Hamiltonians
        ham_frame = ttk.Frame(notebook)
        notebook.add(ham_frame, text="Hamiltonians")
        
        ttk.Label(ham_frame, text="Local Hamiltonian:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        local_entry = ttk.Entry(ham_frame, width=50)
        local_entry.grid(row=0, column=1, padx=5, pady=5)
        local_entry.insert(0, "w*X/2")
        
        ttk.Label(ham_frame, text="Driver Hamiltonian:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        driver_entry = ttk.Entry(ham_frame, width=50)
        driver_entry.grid(row=1, column=1, padx=5, pady=5)
        driver_entry.insert(0, "D")
        
        fields["local"] = local_entry
        fields["driver"] = driver_entry
        
        # Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        def create_qubit():
            try:
                # Get values
                E1 = float(fields["E1"].get())
                E2 = float(fields["E2"].get())
                Omega = float(fields["Omega"].get())
                detuning = float(fields["detuning"].get())
                phi = float(fields["phi"].get())
                alpha_real = float(fields["alpha_real"].get())
                alpha_img = float(fields["alpha_img"].get())
                beta_real = float(fields["beta_real"].get())
                beta_img = float(fields["beta_img"].get())
                tolarence = float(fields["tolarence"].get())
                local = fields["local"].get()
                driver = fields["driver"].get()
                
                # Create qubit
                q = qubit(E1, E2, Omega, detuning, phi, 
                         alpha_real, alpha_img, beta_real, beta_img,
                         tolarence, local, driver)
                
                self.qubits.append(q)
                self.update_qubit_list()
                
                self.print_to_console(f"✅ Created qubit {len(self.qubits)}: {q}", "success")
                self.update_status(f"Created qubit {len(self.qubits)}")
                
                popup.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create qubit: {e}")
                
        ttk.Button(button_frame, text="Create", command=create_qubit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
        
    def update_qubit_list(self):
        """Update the qubit list display"""
        # Clear existing widgets
        for widget in self.qubit_frame.winfo_children():
            widget.destroy()
            
        # Add qubit buttons
        for i, q in enumerate(self.qubits):
            frame = ttk.Frame(self.qubit_frame)
            frame.pack(fill=tk.X, pady=2)
            
            # Qubit button
            btn = ttk.Button(frame, text=f"Qubit {i+1}", 
                           command=lambda idx=i: self.show_qubit_details(idx))
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Delete button
            del_btn = ttk.Button(frame, text="✖", width=3,
                               command=lambda idx=i: self.delete_qubit(idx))
            del_btn.pack(side=tk.RIGHT)
            
    def show_qubit_details(self, idx):
        """Show details of selected qubit in console"""
        q = self.qubits[idx]
        self.print_to_console(f"\n{'='*50}", "info")
        self.print_to_console(f"Qubit {idx+1} Details:", "info")
        self.print_to_console(f"  State: {q}", "info")
        self.print_to_console(f"  Energy levels: E1={q.E1}, E2={q.E2}", "info")
        self.print_to_console(f"  ω (angular freq): {q.omega}", "info")
        self.print_to_console(f"  Ω (Rabi freq): {q.Omega}", "info")
        self.print_to_console(f"  Detuning: {q.detuning}", "info")
        self.print_to_console(f"  Phase φ: {q.phi}", "info")
        self.print_to_console(f"  Norm: {q.normalise()}", "info")
        self.print_to_console(f"  Local H: {q.local_hamiltonian}", "info")
        self.print_to_console(f"  Driver H: {q.driver_hamiltonian}", "info")
        self.print_to_console(f"{'='*50}\n", "info")
        
    def delete_qubit(self, idx):
        """Delete a qubit"""
        if messagebox.askyesno("Delete Qubit", f"Delete qubit {idx+1}?"):
            del self.qubits[idx]
            self.update_qubit_list()
            self.print_to_console(f"Deleted qubit {idx+1}", "info")
            self.update_status(f"Deleted qubit {idx+1}")
            
    def clear_all_qubits(self):
        """Reset the workspace so a new simulation can start cleanly."""
        if not messagebox.askyesno("Clear All", "Delete all qubits and reset the current system?"):
            return

        self.qubits.clear()
        self.qubit_buttons.clear()
        self.current_system = None
        self.update_qubit_list()

        from system_final import system
        system.use_monte_carlo = False
        system.noise_model = None
        system.monte_carlo_trajectories = 1

        if hasattr(self, "mc_indicator"):
            self.mc_indicator.config(text="", foreground="black")

        if hasattr(self, "chat"):
            self.chat.clear_chat()

        self.update_status("Workspace reset")
        self.print_to_console("Cleared all qubits and reset simulation memory.", "info")
    
    def show_noise_popup(self):
        """Show popup for Monte Carlo noise parameters"""
        popup = tk.Toplevel(self.root)
        popup.title("Monte Carlo Noise Parameters")
        popup.geometry("450x550")
        popup.transient(self.root)
        popup.grab_set()
        
        ttk.Label(popup, text="Monte Carlo Noise Settings", style='Title.TLabel').pack(pady=10)
        
        # Create frame for entries
        entries_frame = ttk.Frame(popup)
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Noise parameters
        noise_params = {}
        params = [
            ("T1 Rate (amplitude damping):", "0.01", "t1_rate"),
            ("T2 Rate (phase damping):", "0.005", "t2_rate"),
            ("Dephasing Rate:", "0.005", "dephasing_rate"),
            ("Measurement Error:", "0.02", "measurement_error"),
            ("Gate Error:", "0.01", "gate_error"),
            ("Number of Trajectories:", "10", "trajectories")
        ]
        
        for i, (label, default, key) in enumerate(params):
            ttk.Label(entries_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=5)
            entry = ttk.Entry(entries_frame, width=20)
            entry.insert(0, default)
            entry.grid(row=i, column=1, padx=5, pady=5)
            noise_params[key] = entry
        
        # Help text
        help_text = """
        Monte Carlo Noise Explanation:
        • T1: Probability of |1⟩ → |0⟩ decay per time step
        • T2: Probability of random phase flip
        • Dephasing: Small random phase rotations
        • Measurement: Bit flip probability during measurement
        • Gate error: Random Pauli error probability
        • Trajectories: Number of random runs to average
        
        Note: dt (time step) is automatically handled
        """
        help_label = ttk.Label(entries_frame, text=help_text, justify=tk.LEFT, foreground="gray")
        help_label.grid(row=len(params), column=0, columnspan=2, pady=10)
        
        def save_noise_settings():
            try:
                from system_final import system, MonteCarloNoise
                
                # Get values
                t1_rate = float(noise_params["t1_rate"].get())
                t2_rate = float(noise_params["t2_rate"].get())
                dephasing_rate = float(noise_params["dephasing_rate"].get())
                measurement_error = float(noise_params["measurement_error"].get())
                gate_error = float(noise_params["gate_error"].get())
                trajectories = int(noise_params["trajectories"].get())
                
                # Create noise model
                system.noise_model = MonteCarloNoise(
                    t1_rate=t1_rate,
                    t2_rate=t2_rate,
                    dephasing_rate=dephasing_rate,
                    measurement_error=measurement_error,
                    gate_error=gate_error
                )
                system.use_monte_carlo = True
                system.monte_carlo_trajectories = trajectories
                
                # Update UI indicator
                self.mc_indicator.config(text="🎲 MC ON", foreground="green")
                
                self.print_to_console(f"✅ Monte Carlo noise enabled:", "success")
                self.print_to_console(f"   T1 rate: {t1_rate}", "info")
                self.print_to_console(f"   T2 rate: {t2_rate}", "info")
                self.print_to_console(f"   Dephasing: {dephasing_rate}", "info")
                self.print_to_console(f"   Measurement error: {measurement_error}", "info")
                self.print_to_console(f"   Gate error: {gate_error}", "info")
                self.print_to_console(f"   Trajectories: {trajectories}", "info")
                
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid noise parameters: {e}")
        
        # Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Enable Noise", command=save_noise_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
            
    def build_system(self):
        """Build the multi-qubit system with optional Monte Carlo noise"""
        if not self.qubits:
            messagebox.showwarning("No Qubits", "Create at least one qubit first.")
            return
            
        # Popup to choose system parameters
        popup = tk.Toplevel(self.root)
        popup.title("Build Quantum System")
        popup.geometry("500x550")
        popup.transient(self.root)
        popup.grab_set()
        
        ttk.Label(popup, text="System Parameters", style='Title.TLabel').pack(pady=10)
        
        # Coupling type
        coupling_frame = ttk.Frame(popup)
        coupling_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(coupling_frame, text="Coupling Type:").pack(side=tk.LEFT)
        coupling_var = tk.StringVar(value="0")
        ttk.Radiobutton(coupling_frame, text="Electric", variable=coupling_var, value="0").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(coupling_frame, text="Magnetic", variable=coupling_var, value="1").pack(side=tk.LEFT, padx=5)
        
        # Hamiltonian type
        ham_frame = ttk.Frame(popup)
        ham_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(ham_frame, text="Hamiltonian Type:").pack(side=tk.LEFT)
        ham_var = tk.StringVar(value="ising")
        ham_combo = ttk.Combobox(ham_frame, textvariable=ham_var, values=['ising', 'heisenberg', 'xx', 'xy'], width=12)
        ham_combo.pack(side=tk.LEFT, padx=5)
        
        # Monte Carlo checkbox
        mc_frame = ttk.Frame(popup)
        mc_frame.pack(fill=tk.X, padx=10, pady=10)
        enable_mc = tk.BooleanVar(value=False)
        
        def on_mc_check():
            if enable_mc.get():
                self.show_noise_popup()
        
        mc_check = ttk.Checkbutton(mc_frame, text="Enable Monte Carlo Noise", variable=enable_mc, 
                                    command=on_mc_check)
        mc_check.pack(anchor=tk.W)
        
        ttk.Label(mc_frame, text="(Click to configure noise parameters)", foreground="gray").pack(anchor=tk.W, padx=20)
        
        # Distances input
        distances_frame = ttk.LabelFrame(popup, text="Pair Distances", padding=5)
        distances_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable frame for distances
        canvas = tk.Canvas(distances_frame, height=200)
        scrollbar = ttk.Scrollbar(distances_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create entry for each pair
        pair_entries = {}
        # In build_system, when creating pair entries, set a better default
        for i in range(len(self.qubits)):
            for j in range(i+1, len(self.qubits)):
                frame = ttk.Frame(scrollable_frame)
                frame.pack(fill=tk.X, pady=2)
                ttk.Label(frame, text=f"Q{i+1}-Q{j+1} distance (nm):").pack(side=tk.LEFT, padx=5)
                entry = ttk.Entry(frame, width=15)
                entry.pack(side=tk.LEFT, padx=5)
                # Use a larger default distance to get reasonable coupling
                # For J ~ 1, distance = (k_elec)^(1/3) ≈ (8.987e9)^(1/3) ≈ 2080
                entry.insert(0, "2080")  # This gives J ≈ 1
                pair_entries[(i, j)] = entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def create_system():
            coupling = int(coupling_var.get())
            ham_type = ham_var.get()
            
            try:
                # Collect distances from entries
                distances = {}
                for (i, j), entry in pair_entries.items():
                    r = float(entry.get())
                    distances[(i, j)] = r
                
                # Create system with distances passed directly
                self.current_system = system(coupling, ham_type, *self.qubits, distances=distances)
                
                self.print_to_console(f"✅ System built with {len(self.qubits)} qubits", "success")
                self.print_to_console(f"   Coupling: {'Electric' if coupling==0 else 'Magnetic'}")
                self.print_to_console(f"   Hamiltonian: {ham_type}")
                
                # Display distances and coupling strengths
                self.print_to_console(f"\nPair distances and coupling strengths:")
                for (i, j), J in self.current_system.pair_distance.items():
                    r = distances[(i, j)]
                    self.print_to_console(f"   Q{i+1}-Q{j+1}: r={r}, J={J:.2e}")
                
                # Update Monte Carlo indicator
                from system_final import system as sys_module
                if enable_mc.get() and sys_module.use_monte_carlo:
                    self.print_to_console(f"   Monte Carlo Noise: ENABLED", "info")
                    self.mc_indicator.config(text="🎲 MC ON", foreground="green")
                else:
                    self.print_to_console(f"   Monte Carlo Noise: DISABLED", "info")
                    self.mc_indicator.config(text="", foreground="black")
                
                popup.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to build system: {e}")
                import traceback
                traceback.print_exc()
        
        # Buttons
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Create System", command=create_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=popup.destroy).pack(side=tk.LEFT, padx=5)
        
    def show_mc_results(self):
        """Display Monte Carlo trajectory results"""
        if not self.current_system:
            self.print_to_console("No system created. Build a system first.", "error")
            return
            
        if not hasattr(self.current_system, 'mc_results') or not self.current_system.mc_results:
            self.print_to_console("No Monte Carlo results available. Run evolution with Monte Carlo enabled first.", "error")
            return
        
        self.print_to_console("\n" + "="*60, "info")
        self.print_to_console("MONTE CARLO TRAJECTORY RESULTS", "info")
        self.print_to_console("="*60, "info")
        self.print_to_console(f"Number of trajectories: {len(self.current_system.mc_results)}", "info")
        self.print_to_console(f"Noise parameters:", "info")
        
        if hasattr(self.current_system, 'noise_model') and self.current_system.noise_model:
            noise = self.current_system.noise_model
            self.print_to_console(f"  T1 rate: {noise.t1_rate}", "info")
            self.print_to_console(f"  T2 rate: {noise.t2_rate}", "info")
            self.print_to_console(f"  Dephasing rate: {noise.dephasing_rate}", "info")
            self.print_to_console(f"  Measurement error: {noise.measurement_error}", "info")
            self.print_to_console(f"  Gate error: {noise.gate_error}", "info")
        
        # Calculate statistics from trajectories
        final_states = []
        final_probabilities = []
        
        for traj in self.current_system.mc_results:
            # Get probabilities for each basis state - use .abs2() instead of abs()
            probs = [amp.abs2() for amp in traj]
            most_likely = max(range(len(probs)), key=lambda i: probs[i])
            final_states.append(most_likely)
            final_probabilities.append(probs)
        
        # Count frequencies
        from collections import Counter
        counts = Counter(final_states)
        
        self.print_to_console("\n📊 FINAL STATE DISTRIBUTION:", "info")
        self.print_to_console("-"*40, "info")
        for state, count in sorted(counts.items()):
            state_str = format(state, f'0{self.current_system.no_of_qubits}b')
            prob = count / len(final_states)
            bar_length = int(prob * 40)
            bar = "█" * bar_length + "░" * (40 - bar_length)
            self.print_to_console(f"  |{state_str}⟩: {bar} {count}/{len(final_states)} ({prob:.3f})", "success" if prob > 0.1 else "info")
        
        # Calculate average fidelity (if initial state was known)
        self.print_to_console("\n📈 TRAJECTORY STATISTICS:", "info")
        self.print_to_console("-"*40, "info")
        
        # Calculate average purity across trajectories
        avg_purity = 0
        for probs in final_probabilities:
            purity = sum(p**2 for p in probs)
            avg_purity += purity
        avg_purity /= len(final_probabilities)
        self.print_to_console(f"  Average purity: {avg_purity:.4f}", "info")
        
        # Calculate entropy
        import math
        avg_entropy = 0
        for probs in final_probabilities:
            entropy = -sum(p * math.log(p) if p > 0 else 0 for p in probs)
            avg_entropy += entropy
        avg_entropy /= len(final_probabilities)
        self.print_to_console(f"  Average von Neumann entropy: {avg_entropy:.4f}", "info")
        
        # Show some sample trajectories
        self.print_to_console("\n🔬 SAMPLE TRAJECTORIES (first 5):", "info")
        self.print_to_console("-"*40, "info")
        for idx in range(min(5, len(self.current_system.mc_results))):
            probs = final_probabilities[idx]
            most_likely = final_states[idx]
            state_str = format(most_likely, f'0{self.current_system.no_of_qubits}b')
            self.print_to_console(f"  Trajectory {idx+1}: Most likely |{state_str}⟩ (p={probs[most_likely]:.3f})", "info")
        
        self.print_to_console("\n" + "="*60, "info")
    def apply_gate(self):
        """Apply gate to the system"""
        if not self.current_system:
            messagebox.showwarning("No System", "Build a system first.")
            return
            
        try:
            qubits_str = self.gate_qubits_entry.get()
            qubits = [int(x.strip()) for x in qubits_str.split(',')]
            gate = self.gate_combo.get()
            self.current_system.apply_operator(qubits, gate)
            self.print_to_console(f"Applied {gate} to qubits {qubits}", "success")
        except Exception as e:
            self.print_to_console(f"Error applying gate: {e}", "error")
            
    def run_evolution(self):
        """Run time evolution"""
        if not self.current_system:
            messagebox.showwarning("No System", "Build a system first.")
            return
            
        try:
            total_time = float(self.evolve_time.get())
            steps = int(self.evolve_steps.get())
            self.update_status(f"Evolving system for {total_time} units...")
            self.print_to_console(f"Starting evolution: total_time={total_time}, steps={steps}", "info")
            
            # Check if Monte Carlo is enabled
            from system_final import system as sys_module
            if sys_module.use_monte_carlo:
                self.print_to_console(f"🎲 Monte Carlo mode: {sys_module.monte_carlo_trajectories} trajectories", "info")
            
            def evolve_thread():
                try:
                    self.current_system.evolve(total_time, steps)
                    self.print_to_console("Evolution complete!", "success")
                    
                    # If Monte Carlo was used, show quick summary
                    if sys_module.use_monte_carlo and hasattr(self.current_system, 'mc_results') and self.current_system.mc_results:
                        self.print_to_console(f"\n📊 Quick Monte Carlo Summary:", "info")
                        self.print_to_console(f"   Ran {len(self.current_system.mc_results)} trajectories", "info")
                        self.print_to_console(f"   Click 'MC Results' button for detailed statistics", "info")
                    
                    self.update_status("Ready")
                except Exception as e:
                    self.print_to_console(f"Evolution error: {e}", "error")
                    self.update_status("Error")
                    
            threading.Thread(target=evolve_thread, daemon=True).start()
        except Exception as e:
            self.print_to_console(f"Invalid evolution parameters: {e}", "error")
            
    def measure_system(self):
        """Measure the system"""
        if not self.current_system:
            messagebox.showwarning("No System", "Build a system first.")
            return
        result = self.current_system.collapse_all()
        self.print_to_console(f"Measurement result: |{result}⟩", "success")
        
    def show_state_vector(self):
        """Show current system state vector"""
        if self.current_system:
            self.print_to_console("", "info")
            self.print_matrix_to_console(self.current_system.state_vector, identity="Current State Vector", basis_labels=True)
        else:
            self.print_to_console("No system created. Build a system first.", "error")
            
    def show_hamiltonian(self):
        """Show current Hamiltonian"""
        if self.current_system:
            self.print_to_console("", "info")
            self.print_matrix_to_console(self.current_system.interaction_hamiltonian, identity="Interaction Hamiltonian")
        else:
            self.print_to_console("No system created. Build a system first.", "error")
            
    def show_logs(self):
        """Show log file viewer"""
        # [Same as previous]
        popup = tk.Toplevel(self.root)
        popup.title("Log Viewer")
        popup.geometry("800x600")
        
        top_frame = ttk.Frame(popup)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def open_log_file():
            filename = filedialog.askopenfilename(
                title="Open Log File",
                filetypes=[("Log files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                try:
                    with open(filename, 'r') as f:
                        log_text.delete(1.0, tk.END)
                        log_text.insert(1.0, f.read())
                except Exception as e:
                    log_text.insert(1.0, f"Error reading file: {e}")
                    
        ttk.Button(top_frame, text="Open Log File", command=open_log_file).pack(side=tk.LEFT, padx=5)
        
        def refresh_log():
            try:
                with open('logging.txt', 'r') as f:
                    log_text.delete(1.0, tk.END)
                    log_text.insert(1.0, f.read())
            except FileNotFoundError:
                log_text.delete(1.0, tk.END)
                log_text.insert(1.0, "No log file found.")
                
        ttk.Button(top_frame, text="Refresh", command=refresh_log).pack(side=tk.LEFT, padx=5)
        
        def clear_log():
            if messagebox.askyesno("Clear Log", "Clear all logs?"):
                try:
                    with open('logging.txt', 'w') as f:
                        f.write("=== Log cleared at " + str(__import__('datetime').datetime.now()) + " ===\n")
                    refresh_log()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear log: {e}")
                    
        ttk.Button(top_frame, text="Clear Log", command=clear_log).pack(side=tk.LEFT, padx=5)
        
        log_text = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=('Courier', 10))
        log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        refresh_log()
        
    def clear_logs(self):
        """Clear the main log file"""
        if messagebox.askyesno("Clear Logs", "Clear the main log file?"):
            try:
                with open('logging.txt', 'w') as f:
                    f.write("=== Log cleared at " + str(__import__('datetime').datetime.now()) + " ===\n")
                self.print_to_console("Log file cleared.", "success")
            except Exception as e:
                self.print_to_console(f"Failed to clear log: {e}", "error")
        
    def show_help(self):
        """Show help popup"""
        popup = tk.Toplevel(self.root)
        popup.title("Help - Quantum Simulation Studio")
        popup.geometry("700x600")
        
        help_text = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=('Arial', 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
        ==================== QUANTUM SIMULATION STUDIO HELP ====================
        
        OVERVIEW:
        ------------------------------------------------------------------------
        This application allows you to simulate multi-qubit quantum systems.
        
        GETTING STARTED:
        ------------------------------------------------------------------------
        1. Create qubits using the "NEW QUBIT" button.
        2. Build a system using the "BUILD SYSTEM" button.
        3. Apply quantum gates, evolve the system, and measure.
        
        COMMAND PROMPT:
        ------------------------------------------------------------------------
        The command prompt at the bottom accepts Windows-like shell commands:
        - dir / ls        : List directory contents
        - cd <dir>        : Change directory
        - mkdir <dir>     : Create directory
        - echo <text>     : Print text
        - type <file>     : Display file contents
        - python <file>   : Run Python script
        - Any command supported by your OS shell.
        
        QUANTUM OPERATIONS PANEL:
        ------------------------------------------------------------------------
        - Apply Gate: Enter qubit indices (e.g., "0" or "0,1") and select gate.
        - Evolve: Set total time and number of steps, then click "Run Evolution".
        - Measure: Collapse the system to a basis state.
        - Show State/Hamiltonian: Display the current quantum state or Hamiltonian.
        
        SYSTEM PARAMETERS:
        ------------------------------------------------------------------------
        - Coupling Type: Electric (1/r³) or Magnetic (1/r³ with constant).
        - Hamiltonian Types:
          * ising: σz⊗σz interaction
          * heisenberg: σx⊗σx + σy⊗σy + σz⊗σz
          * xx: σx⊗σx
          * xy: σx⊗σx + σy⊗σy
        - Pair Distances: Enter distances between qubits (in same units as constants).
        
        QUANTUM GATES:
        ------------------------------------------------------------------------
        Single-qubit: H, X, Y, Z, I, S, T
        Two-qubit: CNOT, SWAP
        
        TIPS:
        ------------------------------------------------------------------------
        - Click on qubit names to see their details.
        - Use the Logs menu to view simulation logs.
        - Save sessions to .qsim files for later use.
        - All console output is automatically saved to logging.txt.
        """
        
        help_text.insert(1.0, help_content)
        help_text.config(state=tk.DISABLED)
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Quantum Simulation Studio\nVersion 1.0\n\nA multi-qubit quantum simulator with GUI.\nDeveloped with Python and Tkinter.")
        
    def save_session(self):
        """Save current session"""
        filename = filedialog.asksaveasfilename(
            title="Save Session",
            defaultextension=".qsim",
            filetypes=[("Quantum Session", "*.qsim"), ("All files", "*.*")]
        )
        if filename:
            try:
                import pickle
                session_data = {
                    'qubits': self.qubits,
                    'current_system': self.current_system
                }
                with open(filename, 'wb') as f:
                    pickle.dump(session_data, f)
                self.print_to_console(f"Session saved to {filename}", "success")
            except Exception as e:
                self.print_to_console(f"Failed to save session: {e}", "error")
                
    def load_session(self):
        """Load saved session"""
        filename = filedialog.askopenfilename(
            title="Load Session",
            filetypes=[("Quantum Session", "*.qsim"), ("All files", "*.*")]
        )
        if filename:
            try:
                import pickle
                with open(filename, 'rb') as f:
                    session_data = pickle.load(f)
                self.qubits = session_data['qubits']
                self.current_system = session_data['current_system']
                self.update_qubit_list()
                self.print_to_console(f"Session loaded from {filename}", "success")
                self.print_to_console(f"Loaded {len(self.qubits)} qubits", "info")
            except Exception as e:
                self.print_to_console(f"Failed to load session: {e}", "error")
                
    def __del__(self):
        """Restore stdout on exit"""
        sys.stdout = self.old_stdout

def main():
    root = tk.Tk()
    app = QuantumUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
