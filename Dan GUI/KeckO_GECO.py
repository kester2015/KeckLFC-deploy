#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
from collections import deque
import os

from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scipy.ndimage import gaussian_filter1d

# ----------------------------------------------------------------------
# Dummy GUI: copy of LfcMonitorGUI with server parts removed/mocked
# ----------------------------------------------------------------------
class DummyLfcMonitorGUI:
    def __init__(self, root):
        self.root = root
        
        self.pending_action    = None
        self.first_update_done = False
        self.log_lines         = deque(maxlen=10)
        self.current_state     = "FULL COMB"  # Track current LFC state (start in FULL COMB)
        self.dialog_active     = False  # Flag to pause updates during dialogs

        root.title("KeckO GECO - Frequency comb control")
        root.geometry("1280x900")

        # -- Tabs --
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.tab_control = ttk.Frame(self.notebook)
        self.tab_monitoring = ttk.Frame(self.notebook)
        self.tab_advanced = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_control, text="Main")
        self.notebook.add(self.tab_monitoring, text="Monitoring")
        self.notebook.add(self.tab_advanced, text="Advanced")
        
        # Temperature data storage (for plotting history)
        self.temp_history = {
            'time': deque(maxlen=100),
            'glycol_rack_in': deque(maxlen=100),
            'glycol_rack_out': deque(maxlen=100),
            'glycol_eocb_in': deque(maxlen=100),
            'glycol_eocb_out': deque(maxlen=100),
            'glycol_flb_in': deque(maxlen=100),
            'glycol_flb_out': deque(maxlen=100),
            'glycol_rfamp1_in': deque(maxlen=100),
            'glycol_rfamp1_out': deque(maxlen=100),
            'glycol_rfamp2_in': deque(maxlen=100),
            'glycol_rfamp2_out': deque(maxlen=100),
            'rack_top': deque(maxlen=100),
            'rack_mid': deque(maxlen=100),
            'rack_bot': deque(maxlen=100),
            'edfa_27': deque(maxlen=100),
            'edfa_23': deque(maxlen=100),
            'edfa_13': deque(maxlen=100),
            'filter_cav': deque(maxlen=100),
            'flattener': deque(maxlen=100),
            'ppln': deque(maxlen=100),
            'waveguide': deque(maxlen=100),
        }
        
        # Servo Monitoring Data
        self.servo_history = deque(maxlen=60)
        self.trans_power_history = deque(maxlen=60)
        self.servo_output_val = 5.0 # Mid-range start
        self.trans_power_val = 1.0 # Normalized
        for _ in range(60): # Pre-fill with flat data
            self.servo_history.append(self.servo_output_val)
            self.trans_power_history.append(self.trans_power_val)
            
        self.temp_time_start = datetime.now()
        
        # Minicomb reference spectrum (stored once, doesn't update)
        self.minicomb_reference = None

        # -- Main Content (Control Tab) --
        frame = ttk.Frame(self.tab_control, padding=10)
        frame.pack(fill="both", expand=True)
        # 2-column layout: Col 0 (Left), Col 1 (Right)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # -- Top Left Container: Buttons + Status --
        top_left_frame = ttk.Frame(frame)
        top_left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5), pady=5)
        top_left_frame.columnconfigure(1, weight=1) # Status expands
        
        # 1. Device Control Buttons (inside top_left)
        btn_frame = ttk.LabelFrame(top_left_frame, text="Device control", padding=8)
        btn_frame.grid(row=0, column=0, sticky="ns", padx=(0,5))
        self.control_buttons = []
        btn_texts = ["OFF", "STANDBY", "MINICOMB", "FULL COMB"]
        actions   = ["LFC_OFF", "LFC_STANDBY", "LFC_MINICOMB", "LFC_FULL_COMB"]
        for i, act in enumerate(actions):
            b = ttk.Button(
                btn_frame,
                text=btn_texts[i],
                command=lambda a=act: self.request_action(a),
                state="disabled"
            )
            b.grid(row=i, column=0, sticky="ew", pady=(0,5))
            self.control_buttons.append(b)

        # 2. Status Monitor (inside top_left)
        status_frame = ttk.LabelFrame(top_left_frame, text="Status monitor", padding=8)
        status_frame.grid(row=0, column=1, sticky="nsew")
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Current Status:")\
            .grid(row=0, column=0, sticky="w")
        self.current_status_label = ttk.Label(status_frame, text="--")
        self.current_status_label.grid(row=0, column=1, sticky="w")

        self.status_items = [
            ("LFC_TEMP_MONITOR",   "TEMP monitor"),
            ("LFC_RFOSCI_MONITOR", "RF Oscillator"),
            ("AMPLIFIER_MONITOR",  "Amplifier Monitor"),
            ("INTERLOCK_MONITOR",  "Interlock Monitor"),
        ]
        self.indicator_ids = {}
        for idx, (kw, txt) in enumerate(self.status_items, start=1):
            ttk.Label(status_frame, text=txt + ":")\
                .grid(row=idx, column=0, sticky="w")
            c = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
            oval = c.create_oval(2, 2, 18, 18, fill="gray")
            c.grid(row=idx, column=1, sticky="w", padx=5)
            self.indicator_ids[kw] = (c, oval)

        idx += 1
        ttk.Label(status_frame, text="Repetition Rate:")\
            .grid(row=idx, column=0, sticky="w")
        self.rr_label = ttk.Label(status_frame, text="-- GHz")
        self.rr_label.grid(row=idx, column=1, sticky="w")

        idx += 1
        ttk.Label(status_frame, text="Last Update:")\
            .grid(row=idx, column=0, sticky="w")
        self.last_update_label = tk.Label(
            status_frame, text="--", fg="red"
        )
        self.last_update_label.grid(row=idx, column=1, sticky="w")

        # -- MiniComb Panel (Left Half) --
        minicomb_frame = ttk.LabelFrame(frame, text="Minicomb Monitor", padding=8)
        minicomb_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", pady=(10,0), padx=(0,5))
        minicomb_frame.columnconfigure(0, weight=1) # Ensure content centers/expands
        
        # Stats Labels
        stats_frame = ttk.Frame(minicomb_frame)
        stats_frame.pack(side="top", fill="x", pady=(0,5))
        
        self.lbl_center_wl = ttk.Label(stats_frame, text="Center Wavelength: -- nm", font=("Arial", 12, "bold"))
        self.lbl_center_wl.pack(anchor="center", pady=2)
        
        self.lbl_width = ttk.Label(stats_frame, text="10 dB Width: -- nm", font=("Arial", 12, "bold"))
        self.lbl_width.pack(anchor="center", pady=2)

        # Plot Frame for Minicomb
        self.trace_frame = ttk.Frame(minicomb_frame)
        self.trace_frame.pack(side="top", fill="both", expand=True)

        # -- Full Comb Panel (Right Half) --
        fullcomb_frame = ttk.LabelFrame(frame, text="Full Comb Monitor", padding=8)
        fullcomb_frame.grid(row=1, column=1, sticky="nsew", pady=(10,0), padx=(5,0))
        fullcomb_frame.columnconfigure(0, weight=1)
        
        # Stats Labels for Full Comb
        fullcomb_stats_frame = ttk.Frame(fullcomb_frame)
        fullcomb_stats_frame.pack(side="top", fill="x", pady=(0,5))
        
        self.lbl_flattened_region = ttk.Label(fullcomb_stats_frame, text="Flattened Region: -- nm to -- nm", font=("Arial", 11, "bold"))
        self.lbl_flattened_region.pack(anchor="center", pady=2)
        
        # Plot Frame for Full Comb
        self.fulltrace_frame = ttk.Frame(fullcomb_frame)
        self.fulltrace_frame.pack(side="top", fill="both", expand=True)

        # Make columns 0 and 1 equal width for 50/50 split
        frame.columnconfigure(0, weight=1) # Left half
        frame.columnconfigure(1, weight=1) # Right half
        frame.columnconfigure(2, weight=0)
        
        # -- Logo in Lower Right (Shifted down due to minicomb) --
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(script_dir, "kecko.png")
            
            pil_img = Image.open(logo_path)
            
            # User has manually cropped the image, so we skip auto-cropping.
            
            # Resize smaller for "little box" (e.g. height 80)
            base_height = 120 # User requested larger
            w_percent = (base_height / float(pil_img.size[1]))
            w_size = int((float(pil_img.size[0]) * float(w_percent)))
            pil_img = pil_img.resize((w_size, base_height), Image.Resampling.LANCZOS)
            
            self.logo_img = ImageTk.PhotoImage(pil_img)
            logo_label = tk.Label(frame, image=self.logo_img)
            # Grid in row 2 (below minicomb), column 2. 
            logo_label.grid(row=2, column=1, sticky="se", padx=10, pady=10)
            
            # Ensure row 2 allows expansion if needed, though usually minimal
            frame.rowconfigure(2, weight=0)
            
        except Exception as e:
            print(f"Warning: Could not load logo: {e}")
            tk.Label(frame, text="(Logo invalid)").grid(row=2, column=2, sticky="se")

        # -- Right: Log --
        # -- Right: Log (Top Right) --
        log_frame = ttk.LabelFrame(frame, text="Log", padding=8)
        log_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.log_listbox = tk.Listbox(
            log_frame, height=10, width=50
        )
        self.log_listbox.grid(row=0, column=0, pady=0)


        # -- Monitoring Tab Content --
        # Create scrollable canvas
        monitor_canvas = tk.Canvas(self.tab_monitoring)
        monitor_scrollbar = ttk.Scrollbar(self.tab_monitoring, orient="vertical", command=monitor_canvas.yview)
        self.monitor_scrollable_frame = ttk.Frame(monitor_canvas)

        self.monitor_scrollable_frame.bind(
            "<Configure>",
            lambda e: monitor_canvas.configure(scrollregion=monitor_canvas.bbox("all"))
        )

        monitor_canvas.create_window((0, 0), window=self.monitor_scrollable_frame, anchor="nw")
        monitor_canvas.configure(yscrollcommand=monitor_scrollbar.set)

        monitor_canvas.pack(side="left", fill="both", expand=True)
        monitor_scrollbar.pack(side="right", fill="y")
        
        # Temperature plot frames (will be populated in create_temp_plots)
        self.temp_plot_frames = {}
        self.create_temp_plots()

        # -- Advanced Tab Content --
        adv_frame = ttk.Frame(self.tab_advanced, padding=10)
        adv_frame.pack(fill="both", expand=True)
        
        # EDFA Controls Section
        edfa_frame = ttk.LabelFrame(adv_frame, text="EDFA Power Controls", padding=10)
        edfa_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        
        self.edfa_controls = {}
        edfa_names = ["27 dBm EDFA", "23 dBm EDFA", "13 dBm EDFA"]
        for i, name in enumerate(edfa_names):
            ttk.Label(edfa_frame, text=name, font=("Arial", 10, "bold")).grid(row=i*3, column=0, sticky="w", pady=(5,0))
            
            ttk.Label(edfa_frame, text="Power:").grid(row=i*3+1, column=0, sticky="w", padx=(10,0))
            power_var = tk.DoubleVar(value=50.0)
            power_slider = ttk.Scale(edfa_frame, from_=0, to=100, orient="horizontal", 
                                    variable=power_var, length=150)
            power_slider.grid(row=i*3+1, column=1, sticky="ew", padx=5)
            power_label = ttk.Label(edfa_frame, text="50.0 mW")
            power_label.grid(row=i*3+1, column=2, sticky="w")
            power_var.trace_add("write", lambda *args, lbl=power_label, var=power_var: 
                               lbl.config(text=f"{var.get():.1f} mW"))
            
            state_var = tk.BooleanVar(value=True)
            state_btn = ttk.Checkbutton(edfa_frame, text="ON", variable=state_var)
            state_btn.grid(row=i*3+2, column=0, columnspan=2, sticky="w", padx=(10,0))
            
            current_label = ttk.Label(edfa_frame, text="Current: 0.5 A", foreground="green")
            current_label.grid(row=i*3+2, column=2, sticky="w")
            
            self.edfa_controls[name] = {'power_var': power_var, 'state_var': state_var, 'current_label': current_label}
        
        # RF Amplifier Controls
        rf_frame = ttk.LabelFrame(adv_frame, text="RF Power Amplifier", padding=10)
        rf_frame.grid(row=0, column=1, sticky="new", padx=5, pady=5)
        
        ttk.Label(rf_frame, text="Amplifier Voltage:").grid(row=0, column=0, sticky="w")
        self.rf_voltage_var = tk.DoubleVar(value=30.0)
        rf_voltage_slider = ttk.Scale(rf_frame, from_=0, to=40, orient="horizontal",
                                     variable=self.rf_voltage_var, length=150)
        rf_voltage_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.rf_voltage_label = ttk.Label(rf_frame, text="30.0 V")
        self.rf_voltage_label.grid(row=0, column=2, sticky="w")
        self.rf_voltage_var.trace_add("write", lambda *args: 
                                      self.rf_voltage_label.config(text=f"{self.rf_voltage_var.get():.1f} V"))
        
        ttk.Label(rf_frame, text="Current:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.rf_current_label = ttk.Label(rf_frame, text="1.2 A", foreground="green")
        self.rf_current_label.grid(row=1, column=1, columnspan=2, sticky="w", pady=(5,0))
        
        # Modulator Controls
        mod_frame = ttk.LabelFrame(adv_frame, text="IM/PM Modulators", padding=10)
        mod_frame.grid(row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5)
        
        ttk.Label(mod_frame, text="IM Bias:").grid(row=0, column=0, sticky="w")
        self.im_bias_var = tk.DoubleVar(value=0.0)
        im_bias_slider = ttk.Scale(mod_frame, from_=-3.0, to=3.0, orient="horizontal",
                                   variable=self.im_bias_var, length=150)
        im_bias_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.im_bias_label = ttk.Label(mod_frame, text="0.0 V")
        self.im_bias_label.grid(row=0, column=2, sticky="w")
        self.im_bias_var.trace_add("write", lambda *args:
                                   self.im_bias_label.config(text=f"{self.im_bias_var.get():.2f} V"))
        
        # Lock IM Bias Checkbutton
        self.im_lock_var = tk.BooleanVar(value=False)
        self.im_lock_chk = ttk.Checkbutton(mod_frame, text="Lock IM Bias", variable=self.im_lock_var)
        self.im_lock_chk.grid(row=0, column=3, sticky="w", padx=10)
        
        # Servo Monitor Plot (Matplotlib)
        servo_fig = plt.Figure(figsize=(4, 2.5), dpi=80)
        self.ax_servo = servo_fig.add_subplot(111)
        self.line_trans, = self.ax_servo.plot([], [], color='blue', label='Transmitted Power')
        self.ax_servo2 = self.ax_servo.twinx()
        self.line_servo, = self.ax_servo2.plot([], [], color='orange', label='Servo Output')
        
        self.ax_servo.set_ylabel("Power (a.u.)", color='blue')
        self.ax_servo2.set_ylabel("Servo (V)", color='orange')
        self.ax_servo.set_ylim(0.8, 1.2)
        self.ax_servo2.set_ylim(0, 10)
        # plt.setp(self.ax_servo.get_yticklabels(), color='blue')
        # plt.setp(self.ax_servo2.get_yticklabels(), color='orange')
        servo_fig.tight_layout()
        
        servo_canvas = FigureCanvasTkAgg(servo_fig, master=mod_frame)
        servo_canvas.get_tk_widget().grid(row=4, column=0, columnspan=4, sticky="nsew", pady=5)
        self.servo_canvas = servo_canvas

        ttk.Label(mod_frame, text="PM Phase:").grid(row=2, column=0, sticky="w", pady=(5,0))
        self.pm_phase_var = tk.DoubleVar(value=35.0)
        pm_phase_slider = ttk.Scale(mod_frame, from_=0, to=50, orient="horizontal",
                                    variable=self.pm_phase_var, length=150)
        pm_phase_slider.grid(row=1, column=1, sticky="ew", padx=5, pady=(5,0))
        self.pm_phase_label = ttk.Label(mod_frame, text="35.0°")
        self.pm_phase_label.grid(row=1, column=2, sticky="w", pady=(5,0))
        self.pm_phase_var.trace_add("write", lambda *args:
                                    self.pm_phase_label.config(text=f"{self.pm_phase_var.get():.1f}°"))
        
        adv_frame.columnconfigure(0, weight=1)
        adv_frame.columnconfigure(1, weight=1)

        # Style
        style = ttk.Style()
        style.configure("TButton", padding=4)

        # Start periodic update
        # Start periodic update
        self.poll_interval = 2000  # milliseconds
        self.populate_history() # Pre-populate logs
        root.after(100, self.update_indicators) 
        
    def populate_history(self):
        # Add realistic historical entries
        now = datetime.now()
        events = [
            (65, "LFC_OFF initiated"),
            (65, "Comb status OFF"),
            (60, "LFC_STANDBY initiated"),
            (60, "Comb status STANDBY"),
            (55, "LFC_MINICOMB initiated"),
            (55, "Comb status MINICOMB"),
            (50, "LFC_FULL_COMB initiated"),
            (50, "Comb status FULL COMB")
        ]
        
        for minutes_ago, msg in events:
            t = now - timedelta(minutes=minutes_ago)
            ts = t.strftime("%Y-%m-%d %H:%M:%S")
            entry = f"[{ts}] {msg}"
            self.log_lines.append(entry)
            self.log_listbox.insert(tk.END, entry)
        self.log_listbox.yview(tk.END) 

    def create_temp_plots(self):
        """Create 7 temperature monitoring plots in scrollable frame"""
        
        # Define plot configurations (6 plots)
        plots_config = [
            ('glycol_eocb', 'Glycol Cooling - EO Comb Board', ['glycol_eocb_in', 'glycol_eocb_out'], ['Inlet', 'Outlet']),
            ('glycol_flb', 'Glycol Cooling - Fiber Laser Board', ['glycol_flb_in', 'glycol_flb_out'], ['Inlet', 'Outlet']),
            ('glycol_rfamp', 'Glycol Cooling - RF Amplifier Blocks', ['glycol_rfamp1_in', 'glycol_rfamp1_out', 'glycol_rfamp2_in', 'glycol_rfamp2_out'], ['Block 1 In', 'Block 1 Out', 'Block 2 In', 'Block 2 Out']),
            ('rack', 'Instrument Rack Environment', ['rack_top', 'rack_mid', 'rack_bot'], ['Top', 'Middle', 'Bottom']),
            ('edfa', 'EDFA Case Temperatures', ['edfa_27', 'edfa_23', 'edfa_13'], ['27 dBm EDFA', '23 dBm EDFA', '13 dBm EDFA']),
            ('optical', 'Optical Component TECs', ['filter_cav', 'flattener', 'ppln', 'waveguide'], ['Filter Cavity', 'Spectral Flattener', 'PPLN Crystal', 'Waveguide']),
        ]
        
        # Create plots in 2-column grid
        for idx, (plot_id, title, data_keys, labels) in enumerate(plots_config):
            row = idx // 2
            col = idx % 2
            
            # Create frame for this plot
            plot_frame = ttk.Frame(self.monitor_scrollable_frame)
            plot_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Create matplotlib figure (shorter to fit all 6 on screen)
            fig = plt.Figure(figsize=(5.5, 2.2), dpi=90)
            ax = fig.add_subplot(111)
            
            # Initial empty plot with styling
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Professional color scheme
            for i, (key, label) in enumerate(zip(data_keys, labels)):
                ax.plot([], [], label=label, color=colors[i % len(colors)], linewidth=1.5, marker='o', markersize=3, markevery=5)
            
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xlabel('Time (s)', fontsize=9)
            ax.set_ylabel('Temperature (°C)', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
            ax.set_ylim(15, 35)  # Reasonable temp range
            
            fig.tight_layout()
            
            # Embed in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Store references
            self.temp_plot_frames[plot_id] = {
                'fig': fig,
                'ax': ax,
                'canvas': canvas,
                'data_keys': data_keys,
                'labels': labels
            }
        
        # Configure grid weights for proper resizing
        for i in range(4):  # 4 rows
            self.monitor_scrollable_frame.rowconfigure(i, weight=1)
        self.monitor_scrollable_frame.columnconfigure(0, weight=1)
        self.monitor_scrollable_frame.columnconfigure(1, weight=1)


    def request_action(self, name):
        # Pause updates during dialog interactions
        self.dialog_active = True
        try:
            # Map action names to states
            state_map = {
                "LFC_OFF": "OFF",
                "LFC_STANDBY": "STANDBY",
                "LFC_MINICOMB": "MINICOMB",
                "LFC_FULL_COMB": "FULL COMB"
            }
            
            target_state = state_map.get(name, "UNKNOWN")
            
            # If already in this state, do nothing
            if self.current_state == target_state:
                self._append_log(f"Already in {target_state} state")
                return
            
            # Password protection for OFF and STANDBY
            if target_state in ["OFF", "STANDBY"]:
                password = simpledialog.askstring(
                    "Password Required",
                    f"Enter password to change to {target_state}:",
                    show='*',
                    parent=self.root
                )
                
                # Simple password check (in real system, use proper authentication)
                if password != "keck":  # Demo password
                    messagebox.showerror("Access Denied", "Incorrect password", parent=self.root)
                    return
            
            # Confirmation for all other transitions
            else:
                # Ask for confirmation
                confirm = messagebox.askyesno(
                    "Confirm State Change",
                    f"Are you sure you want to change from {self.current_state} to {target_state}?",
                    parent=self.root
                )
                
                if not confirm:
                    return
            
            # Execute the action with simulated delay
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._append_log(f"{name} initiated @ {ts}")
            self._append_log(f"Turning comb state to {target_state}...")
            print(f"[Terminal] Initiating action: {name}")
            print(f"[Terminal] Turning comb state to {target_state}...")
            
            # Simulate state transition delay (2 seconds)
            def complete_transition():
                self.current_state = target_state
                self._append_log(f"Comb status {target_state}")
                print(f"[Terminal] Comb status {target_state}")
            
            self.root.after(2000, complete_transition)
        finally:
            # Resume updates
            self.dialog_active = False



    def _append_log(self, text):
        if self.log_listbox.size() >= 10:
            self.log_listbox.delete(0)
        self.log_listbox.insert(tk.END, text)
        self.log_listbox.yview_moveto(1.0)

    def update_temp_plots(self):
        """Update temperature plots with new mock data"""
        
        # Calculate elapsed time
        elapsed = (datetime.now() - self.temp_time_start).total_seconds()
        self.temp_history['time'].append(elapsed)
        
        # Generate realistic mock temperatures
        t = elapsed
        
        # Glycol system: 18-22°C with slow drift
        self.temp_history['glycol_rack_in'].append(20.0 + 0.5 * np.sin(t/100) + np.random.normal(0, 0.1))
        self.temp_history['glycol_rack_out'].append(20.5 + 0.5 * np.sin(t/100) + np.random.normal(0, 0.1))
        self.temp_history['glycol_eocb_in'].append(19.5 + 0.3 * np.sin(t/120) + np.random.normal(0, 0.1))
        self.temp_history['glycol_eocb_out'].append(20.0 + 0.3 * np.sin(t/120) + np.random.normal(0, 0.1))
        self.temp_history['glycol_flb_in'].append(19.8 + 0.4 * np.sin(t/110) + np.random.normal(0, 0.1))
        self.temp_history['glycol_flb_out'].append(20.3 + 0.4 * np.sin(t/110) + np.random.normal(0, 0.1))
        self.temp_history['glycol_rfamp1_in'].append(20.2 + 0.6 * np.sin(t/90) + np.random.normal(0, 0.1))
        self.temp_history['glycol_rfamp1_out'].append(21.0 + 0.6 * np.sin(t/90) + np.random.normal(0, 0.1))
        self.temp_history['glycol_rfamp2_in'].append(20.1 + 0.5 * np.sin(t/95) + np.random.normal(0, 0.1))
        self.temp_history['glycol_rfamp2_out'].append(20.8 + 0.5 * np.sin(t/95) + np.random.normal(0, 0.1))
        
        # Rack temps: 22-28°C with gradient (top warmer)
        self.temp_history['rack_top'].append(27.0 + 0.8 * np.sin(t/150) + np.random.normal(0, 0.2))
        self.temp_history['rack_mid'].append(25.0 + 0.6 * np.sin(t/150) + np.random.normal(0, 0.2))
        self.temp_history['rack_bot'].append(23.5 + 0.5 * np.sin(t/150) + np.random.normal(0, 0.2))
        
        # EDFA case temps: 24-32°C with realistic heating
        self.temp_history['edfa_27'].append(28.0 + 1.0 * np.sin(t/200) + np.random.normal(0, 0.3))
        self.temp_history['edfa_23'].append(26.5 + 0.8 * np.sin(t/180) + np.random.normal(0, 0.3))
        self.temp_history['edfa_13'].append(25.0 + 0.7 * np.sin(t/190) + np.random.normal(0, 0.3))
        
        # Optical components: 20-25°C (TEC-controlled, very stable)
        self.temp_history['filter_cav'].append(22.0 + 0.05 * np.sin(t/300) + np.random.normal(0, 0.02))
        self.temp_history['flattener'].append(21.5 + 0.05 * np.sin(t/280) + np.random.normal(0, 0.02))
        self.temp_history['ppln'].append(23.0 + 0.05 * np.sin(t/290) + np.random.normal(0, 0.02))
        self.temp_history['waveguide'].append(22.5 + 0.05 * np.sin(t/310) + np.random.normal(0, 0.02))
        
        # Update all plots
        time_data = list(self.temp_history['time'])
        
        for plot_id, plot_info in self.temp_plot_frames.items():
            ax = plot_info['ax']
            data_keys = plot_info['data_keys']
            
            # Clear and replot
            ax.clear()
            
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
            for i, (key, label) in enumerate(zip(data_keys, plot_info['labels'])):
                temp_data = list(self.temp_history[key])
                ax.plot(time_data, temp_data, label=label, color=colors[i % len(colors)], 
                       linewidth=1.5, marker='o', markersize=3, markevery=max(1, len(time_data)//20))
            
            # Restore styling
            ax.set_xlabel('Time (s)', fontsize=9)
            ax.set_ylabel('Temperature (°C)', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
            
            # Auto-scale y-axis with some padding
            if len(time_data) > 0:
                all_temps = []
                for key in data_keys:
                    all_temps.extend(list(self.temp_history[key]))
                if all_temps:
                    y_min, y_max = min(all_temps), max(all_temps)
                    y_range = y_max - y_min
                    ax.set_ylim(y_min - 0.2*y_range, y_max + 0.2*y_range)
            
            plot_info['canvas'].draw()

    def update_indicators(self):
        # Skip updates if dialog is active to prevent focus stealing
        if self.dialog_active:
            self.root.after(self.poll_interval, self.update_indicators)
            return
        
        # 0) Display actual current state
        self.current_status_label.config(text=self.current_state)

        # 1) Mock Indicators
        for kw, _ in self.status_items:
            val = 0 # All good
            c, oid = self.indicator_ids[kw]
            color = "green"
            c.itemconfig(oid, fill=color)

        # 2) Mock Repetition Rate
        rr = 16.0 + np.random.uniform(-0.001, 0.001)
        self.rr_label.config(text=f"{rr:.4f} GHz")

        # 3) Last Update
        self.last_update_label.config(
            text=datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
        )

        # 4) Minicomb Trace using EO Physics Model
        for w in self.trace_frame.winfo_children():
            w.destroy()
        
        # --- Physics Simulation ---
        fs = 16e9                   # Comb spacing (16 GHz)
        delta_phi_pm = 35           # PM drive (Controls bandwidth, ~100 teeth)
        delta_phi_im = 0.25 * np.pi  # IM drive (Under-driven to flatten)
        phi_bias = 0.25 * np.pi     # IM Bias (Quadrature bias)
        theta = 0.5 * np.pi         # Phase sync (Critical for symmetry)
        
        # Simulation Settings
        N_points = 2**16 # Slightly reduced for GUI responsiveness
        N_periods = 200  # Capture many cycles for sharp teeth
        T_s = 1/fs
        t = np.linspace(0, N_periods * T_s, N_points, endpoint=False)
        dt = t[1] - t[0]
        
        # --- Math Model ---
        # 1. Phase Modulated Field (The "Carrier" for the comb)
        E_pm = np.exp(1j * delta_phi_pm * np.sin(2 * np.pi * fs * t))
        
        # 2. Intensity Modulator (Acting as the spectral equalizer)
        # We use the field transmission function for an MZM
        T_im = np.cos(delta_phi_im * np.cos(2 * np.pi * fs * t + theta) + phi_bias)
        
        # 3. Combined Output
        E_total = T_im * E_pm
        
        # Spectrum
        spec = np.fft.fftshift(np.fft.fft(E_total))
        
        # ... (rest of broadening logic remains, it works on 'spec')
        pwr_linear = np.abs(spec)**2
        freqs = np.fft.fftshift(np.fft.fftfreq(N_points, d=dt))
        
        # --- Broadening (OSA Response 5 GHz) ---
        target_res_GHz = 10.0
        df_Hz = (freqs[1] - freqs[0])
        
        sigma_GHz = target_res_GHz / 2.355 # FWHM to Sigma
        sigma_points = sigma_GHz * 1e9 / df_Hz
        
        # Convolve linear power with Gaussian
        pwr_broad = gaussian_filter1d(pwr_linear, sigma=sigma_points)
        
        # Convert to dB (Normalized to max 0 or -10 offset?)
        peak_pwr = np.max(pwr_broad)
        S_broad_dB = 10 * np.log10(pwr_broad / peak_pwr + 1e-12) - 10 
        
        # --- Axis Conversion to Wavelength ---
        # Center freq approx 1560nm
        c_light = 299792458
        f_c = c_light / 1560e-9 
        f_abs = f_c + freqs # Hz
        
        wl_m = c_light / f_abs
        wl_nm = wl_m * 1e9
        
        # Filter range for plotting (1550-1570nm = 20 nm span)
        mask = (wl_nm > 1550) & (wl_nm < 1570)
        wl_plot = wl_nm[mask]
        S_plot = S_broad_dB[mask]
        
        # Downsample to simulate OSA resolution (~1 GHz spacing)
        # At 1560 nm: 1 GHz ≈ 0.008 nm (λ²/c * Δf)
        # 20 nm span / 0.008 nm ≈ 2500 points
        target_points = 2500
        downsample_factor = max(1, len(wl_plot) // target_points)
        wl_plot = wl_plot[::downsample_factor]
        S_plot = S_plot[::downsample_factor]
        
        # Add ASE Background (approx -30 dBm level with noise)
        p_comb_lin = 10**(S_plot/10.0)
        # Dynamic noisy background: -30 dBm mean, +/- noise
        noise_bg = np.random.normal(0, 0.5, len(wl_plot))
        p_ase_lin = 10**((-30.0 + noise_bg)/10.0)
        
        S_plot = 10 * np.log10(p_comb_lin + p_ase_lin)
        
        # --- Stats ---
        max_idx = np.argmax(S_plot)
        center_wl_meas = wl_plot[max_idx]
        
        target_val = S_plot[max_idx] - 10
        above = np.where(S_plot > target_val)[0]
        if len(above) > 1:
            # Need to be careful with wavelength sorting (it's inverse freq, so decreasing?)
            # wl_nm is decreasing as freq increases.
            width_nm = abs(wl_plot[above[-1]] - wl_plot[above[0]])
        else:
            width_nm = 0.0

        self.lbl_center_wl.config(text=f"Center WL: {center_wl_meas:.2f} nm")
        self.lbl_width.config(text=f"10 dB Width: {width_nm:.2f} nm")

        # Plot Minicomb
        fig_mc = plt.Figure(figsize=(5,2.5), dpi=100)
        ax_mc = fig_mc.add_subplot(111)
        
        # Store reference spectrum on first update
        if self.minicomb_reference is None and self.current_state in ["MINICOMB", "FULL COMB"]:
            self.minicomb_reference = {'wl': wl_plot.copy(), 'S': S_plot.copy()}
        
        # Always plot reference spectrum (blue, static, shifted up 1 dBm) if available
        if self.minicomb_reference is not None:
            ref_shifted = self.minicomb_reference['S'] + 1.0  # Shift up 1 dBm for visibility
            ax_mc.plot(self.minicomb_reference['wl'], ref_shifted, 
                      color='blue', linewidth=1.0, alpha=0.7, label='Reference')
        
        # Check if minicomb should be active (MINICOMB or FULL COMB states)
        if self.current_state in ["MINICOMB", "FULL COMB"]:
            # Plot live data (red)
            ax_mc.plot(wl_plot, S_plot, color='red', linewidth=1.0, label='Live')
        else:
            # Show baseline in OFF/STANDBY states (spectrometer noise floor)
            baseline = np.full_like(wl_plot, -30.0)  # Background noise level
            noise = np.random.normal(0, 0.5, len(wl_plot))  # Spectrometer noise
            baseline_noisy = baseline + noise
            
            # Plot live baseline with noise (red, same color as active state)
            ax_mc.plot(wl_plot, baseline_noisy, color='red', linewidth=1.0, label='Live') 
        
        
        # Fixed axis limits for all states
        ax_mc.set_ylim(-40, -5)
        ax_mc.set_title("Mini-Comb Spectrum (EO Model)")
        ax_mc.set_xlabel("Wavelength (nm)")
        ax_mc.set_ylabel("Power (dBm)")
        ax_mc.set_xlim(1552.5, 1567.5)  # Zoomed in x-axis limits
        ax_mc.tick_params(axis='x', labelsize=8)  # Smaller x-axis tick labels
        ax_mc.grid(True)
        ax_mc.legend(loc='upper right', fontsize=8)
        fig_mc.tight_layout()
        # ax_mc.invert_xaxis() # Optics convention: frequency increases to right? usually WL increases to right.
        # Matplotlib defaults increasing X. WL array is decreasing. Plot sorts by index.
        # Plotting (wl_plot, S_plot) will just connect points. 
        # But wavelength decreases with index.
        # Let's just plot normally, matplotlib handles axis values. 
        # But if we want high-low, ax.invert_xaxis() isn't needed if we pass sorted WL or matplotlib handles it.
        # Usually standard is low WL (Blue) left, high WL (Red) right.
        
        canvas_mc = FigureCanvasTkAgg(fig_mc, master=self.trace_frame)
        canvas_mc.get_tk_widget().pack(fill="both", expand=True)

        # 5) Full Comb Trace (Right Panel) - MERGED
        for w in self.fulltrace_frame.winfo_children():
            w.destroy()
            
        # Try Loading Real Data
        x_fc = []
        y_base = []
        loaded = False
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(script_dir, "yokogawa.CSV")
            
            if os.path.exists(csv_path):
                with open(csv_path, 'r') as f:
                    lines = f.readlines()
                    
                data_start = False
                for line in lines:
                    if "[TRACE DATA]" in line:
                        data_start = True
                        continue
                    
                    if data_start:
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            try:
                                wl = float(parts[0])
                                pwr = float(parts[1])
                                x_fc.append(wl)
                                y_base.append(pwr)
                            except ValueError:
                                continue
                
                if len(x_fc) > 0:
                    x_fc = np.array(x_fc)
                    y_base = np.array(y_base)
                    # Downsample by factor of 2
                    x_fc = x_fc[::2]
                    y_base = y_base[::2]
                    loaded = True
            else:
                print("Warning: yokogawa.CSV not found.")
                
        except Exception as e:
            print(f"Error reading CSV: {e}")

        # Fallback if load failed
        if not loaded:
             x_fc = np.linspace(1500, 3000, 300)  # Reduced from 600
             hump = -10 - 20 * ((x_fc - 1580)/100)**2  
             slope = -12 - (x_fc - 1600) * (45/1100) 
             y_base = np.maximum(hump, slope)
             y_base[x_fc > 2800] -= (x_fc[x_fc > 2800] - 2800) * 0.5
             y_base += 2.0 * np.sin(x_fc * 0.05) 

        # Add Noise
        noise_fc = np.random.normal(0, 0.5, len(y_base)) # Less noise since real data is noisy? or user wants "plenty of noise"
        y_unflat = y_base + noise_fc
        
        # Flattened (Purple mimic)
        # Target needs to be appropriate for the CSV data levels.
        # CSV data peaks around -10, drops to -70.
        target = -40
        ideal_att = y_unflat - target
        real_att = np.clip(ideal_att, 0, 25)
        y_flat = y_unflat - real_att + np.random.normal(0, 0.5, len(y_base))
        
        # Calculate flattened region (where spectrum is within 3 dB of target)
        target_level = -40
        tolerance = 3  # dB
        flat_mask = np.abs(y_flat - target_level) < tolerance
        if np.any(flat_mask):
            flat_indices = np.where(flat_mask)[0]
            flat_start = x_fc[flat_indices[0]]
            flat_end = x_fc[flat_indices[-1]]
            self.lbl_flattened_region.config(text=f"Flattened Region: {flat_start:.0f} nm to {flat_end:.0f} nm")
        else:
            self.lbl_flattened_region.config(text="Flattened Region: N/A")

        fig_fc = plt.Figure(figsize=(5,4), dpi=100)
        ax_fc = fig_fc.add_subplot(111) # Single subplot
        
        # Check if full comb should be active (only in FULL COMB state)
        if self.current_state == "FULL COMB":
            ax_fc.plot(x_fc, y_flat, color='purple', label="Arc Optics", linewidth=0.8)
            ax_fc.plot(x_fc, y_unflat, color='green', label="Arc Optics minus flattener mask", linewidth=0.8)
        else:
            # Show baseline in OFF/STANDBY/MINICOMB states (spectrometer noise floor)
            baseline = np.full_like(x_fc, -58.0)
            noise = np.random.normal(0, 0.5, len(x_fc))  # Spectrometer noise
            baseline_noisy = baseline + noise
            
            # Plot both traces with noise (same colors as active state)
            ax_fc.plot(x_fc, baseline_noisy, color='purple', label="Arc Optics", linewidth=0.8)
            # Add independent noise for second trace
            noise2 = np.random.normal(0, 0.5, len(x_fc))
            baseline_noisy2 = baseline + noise2
            ax_fc.plot(x_fc, baseline_noisy2, color='green', label="Arc Optics minus flattener mask", linewidth=0.8)
        
        ax_fc.set_title("Full Comb Spectrum")
        ax_fc.set_xlabel("Wavelength (nm)")
        ax_fc.set_ylabel("Power (dBm)")
        ax_fc.set_xlim(1500, 2800)  # Fixed x-axis limits
        ax_fc.grid(True)
        ax_fc.set_ylim(-65, 0) # Adjusted for CSV range
        ax_fc.legend(loc="upper right")
        
        fig_fc.tight_layout()
        
        canvas_fc = FigureCanvasTkAgg(fig_fc, master=self.fulltrace_frame)
        canvas_fc.get_tk_widget().pack(fill="both", expand=True)

        # 6) Enable control buttons
        if not self.first_update_done:
            for b in self.control_buttons:
                b.config(state="normal")
            self.first_update_done = True
        
        # Update Servo Monitor Plot
        if hasattr(self, 'servo_canvas'):
            try:
                # Random walk for servo output
                drift = (np.random.random() - 0.5) * 0.4 
                self.servo_output_val += drift
                self.servo_output_val = max(0, min(10, self.servo_output_val))
                
                # Constant transmitted power with noise
                self.trans_power_val = 1.0 + np.random.normal(0, 0.01)
                
                # Update deques
                self.servo_history.append(self.servo_output_val)
                self.trans_power_history.append(self.trans_power_val)
                
                # Draw
                self.line_trans.set_data(range(len(self.trans_power_history)), self.trans_power_history)
                self.line_servo.set_data(range(len(self.servo_history)), self.servo_history)
                
                self.ax_servo.set_xlim(0, max(60, len(self.trans_power_history)))
                self.servo_canvas.draw()
            except Exception as e:
                pass # limits or something might be initializing
            
        # 7) Update temperature plots
        self.update_temp_plots()

        # Schedule next update
        self.root.after(self.poll_interval, self.update_indicators)

if __name__ == "__main__":
    print("Starting Dummy LFC GUI...")
    root = tk.Tk()
    app  = DummyLfcMonitorGUI(root)
    root.mainloop()
    print("Dummy GUI closed.")
