import datetime
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

import data_stub
from layout import ModeAwareMixin, VB_FIELD_BG, VB_FONT, VB_FONT_BOLD, VB_FORM_BG, client_size, make_frame, place

MSG_TITLE = "IMT LampElectrical Probing"


class RuntimeForm(tk.Toplevel, ModeAwareMixin):
    """Recreation of frmRunTime.frm - the main probing screen shown after GO."""

    def __init__(self, master, recipe_name, wafer_id, operator_id, process_step, mode):
        tk.Toplevel.__init__(self, master)
        ModeAwareMixin.__init__(self)

        self.recipe_name = recipe_name
        self.wafer_id = wafer_id
        self.operator_id = operator_id
        self.process_step = process_step
        self.mode_var = tk.StringVar(value=mode)  # "Full" or "Manual", carried over from frmOpening

        self.chk_flush_var = tk.BooleanVar(value=False)
        self.chk_suppress_debug_var = tk.BooleanVar(value=False)  # no Value=1 in the .frm -> unchecked
        self.chk_db_save_var = tk.BooleanVar(value=False)
        self.chk_save_text_var = tk.BooleanVar(value=False)  # no Value=1 in the .frm -> unchecked
        self.jump_var = tk.StringVar(value="JumpFromAlign")  # optJumpFromAlign is TabIndex 10,
        # lower than optNoJump's 11, so it's the VB6 runtime default per the same rule used
        # on frmOpening's Option1/Option2.

        # HPIB_Relay1 / HPIB_2001X / HPIB_Keithley2400 - the three Agt3494ALib.Agt3494A
        # ActiveX instances on the real form, replaced here by real pyvisa-backed
        # drivers (data_stub.build_hpib_instruments(), 2026-07-22) rather than the
        # AGT3494A.OCX ActiveX control itself, which Lampexe never actually needed -
        # see that function's docstring for the address/reachability details. Each
        # driver already opens (or fails to open) its real GPIB session in its own
        # constructor, using the fixed address in instruments.yaml, which is why
        # this happens here rather than being deferred to _form_load() the way the
        # real exe's DB-driven .Address assignment was.
        hpib = data_stub.build_hpib_instruments()
        self.hpib_2001x = hpib["2001X"]
        self.hpib_relay1 = hpib["Relay1"]
        self.hpib_keithley2400 = hpib["Keithley2400"]
        self._hpib_by_name = hpib

        self.title("LampElectrical Run Time")  # frmRunTime.Caption
        w, h = client_size(11625, 9795)  # frmRunTime.ClientWidth/ClientHeight
        self.geometry(f"{w}x{h}")
        self.configure(bg=VB_FORM_BG)

        self._run_in_progress = False
        self._align_confirmed = False

        self._build_controls()
        self.apply_mode(self.mode_var.get())
        self._form_load()

    # -- layout -------------------------------------------------------

    def _build_controls(self):
        # lblInfo "Label1" - L120 T240 W2655 H615 - status/title, two lines worth of height
        self.lbl_info = tk.Label(
            self, text="", bg=VB_FORM_BG, font=VB_FONT, anchor="nw", justify="left"
        )
        place(self.lbl_info, 120, 240, 2655, 615)

        # cmdGo "GO" - L1800 T1800 W1500 H615
        self.cmd_go = tk.Button(self, text="GO", font=VB_FONT_BOLD, command=self.cmd_go_click)
        place(self.cmd_go, 1800, 1800, 1500, 615)

        # chkFlush - L120 T1800 W1575 H615
        chk_flush = tk.Checkbutton(
            self,
            text="Cache the data for later 'Flush'",
            variable=self.chk_flush_var,
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
            justify="left",
            wraplength=85,
        )
        place(chk_flush, 120, 1800, 1575, 615)

        # cmdRevert "Change to Engineering Mode" - L1800 T3240 W1500 H615
        self.cmd_revert = tk.Button(
            self, text="Change to Engineering Mode", font=VB_FONT, wraplength=95, command=self.cmd_revert_click
        )
        place(self.cmd_revert, 1800, 3240, 1500, 615)

        # chkSuppressDebug - L1800 T4080 W2295 H255
        chk_suppress = tk.Checkbutton(
            self,
            text="Suppress Debug Messages",
            variable=self.chk_suppress_debug_var,
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
        )
        place(chk_suppress, 1800, 4080, 2295, 255)

        self._build_frame1_engineering_mode()
        self._build_frame2_switch_powering()

        # Line1 - red divider (BorderColor &HFF& = VB6 &HBBGGRR& -> red), separates the
        # controls area above from the txtData log below.
        line1 = tk.Frame(self, bg="red", height=3)
        self._place_hline(line1, x1=0, y=7560, x2=11040, bordercolor="red", borderwidth=3)

        # txtData - L0 T7680 W11055 H1815, MultiLine + Locked (readonly)
        self.txt_data = tk.Text(self, bg=VB_FIELD_BG, font=("Courier New", 9), state="disabled", wrap="word")
        place(self.txt_data, 0, 7680, 11055, 1815)

    def _place_hline(self, frame, x1, y, x2, bordercolor, borderwidth):
        from layout import tw

        frame.configure(bg=bordercolor, height=borderwidth)
        frame.place(x=tw(x1), y=tw(y), width=tw(x2 - x1), height=borderwidth)

    def _build_frame1_engineering_mode(self):
        # Frame1 "Engineering Mode" - L4080 T120 W6975 H3495 - Tag="View=Manual;"
        frame1 = make_frame(self, "Engineering Mode", 4080, 120, 6975, 3495, font=VB_FONT)
        self.register_view_tag(frame1, "Manual", 4080, 120, 6975, 3495)

        opt_jump = tk.Radiobutton(
            frame1,
            text="Make the jump from the align site to the chosen die.",
            variable=self.jump_var,
            value="JumpFromAlign",
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
        )
        place(opt_jump, 480, 480, 4335, 255)

        opt_no_jump = tk.Radiobutton(
            frame1,
            text="Prober stage is already at the correct die. No initial jump.",
            variable=self.jump_var,
            value="NoJump",
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
            justify="left",
            wraplength=290,
        )
        place(opt_no_jump, 480, 840, 4455, 375)

        line2 = tk.Frame(frame1, bg="black", height=1)
        self._place_hline(line2, x1=240, y=1440, x2=6600, bordercolor="black", borderwidth=1)

        lbl_filename = tk.Label(frame1, text="File Name", bg=VB_FORM_BG, font=VB_FONT, anchor="w")
        place(lbl_filename, 360, 2400, 855, 255)

        self.txt_file_name = tk.Entry(frame1, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_file_name, 1320, 2400, 5295, 285)

        chk_save_text = tk.Checkbutton(
            frame1,
            text="Save a text copy of session measurements in file.",
            variable=self.chk_save_text_var,
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
        )
        place(chk_save_text, 480, 2040, 4215, 255)

        self.cmd_view = tk.Button(frame1, text="View", font=VB_FONT, command=self.cmd_view_click)
        place(self.cmd_view, 4680, 2040, 1575, 255)

        chk_db_save = tk.Checkbutton(
            frame1,
            text="Save the session measurements to the database.",
            variable=self.chk_db_save_var,
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
            state="disabled",  # Enabled = 0 in the .frm
        )
        place(chk_db_save, 480, 1680, 3855, 255)

        lbl_wafer = tk.Label(frame1, text="Wafer ID", bg=VB_FORM_BG, font=VB_FONT, anchor="w")
        place(lbl_wafer, 360, 3000, 855, 255)

        self.txt_wafer_id_frame1 = tk.Entry(frame1, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_wafer_id_frame1, 1320, 3000, 1215, 285)

        # comboDies - L4800 T480 W2055 H315
        self.combo_dies = ttk.Combobox(frame1, font=VB_FONT, state="readonly")
        place(self.combo_dies, 4800, 480, 2055, 315)

    def _build_frame2_switch_powering(self):
        # Frame2 "Switch Powering" - L4080 T4200 W5415 H3135 - Tag="View=Manual;"
        frame2 = make_frame(self, "Switch Powering", 4080, 4200, 5415, 3135, font=VB_FONT)
        self.register_view_tag(frame2, "Manual", 4080, 4200, 5415, 3135)

        lbl1 = tk.Label(frame2, text="Voltage", bg=VB_FORM_BG, font=VB_FONT, anchor="w")
        place(lbl1, 120, 480, 615, 255)
        self.combo_voltage = ttk.Combobox(frame2, font=VB_FONT)
        place(self.combo_voltage, 960, 480, 1095, 315)

        lbl3 = tk.Label(frame2, text="Delays (mSec)", bg=VB_FORM_BG, font=VB_FONT, anchor="center")
        place(lbl3, 3720, 240, 1215, 255)

        lbl5 = tk.Label(frame2, text="NOT USED", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(lbl5, 2520, 480, 1335, 255)
        self.txt_delay1 = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_delay1, 3960, 480, 975, 285)

        lbl6 = tk.Label(frame2, text="After relay set, pre Ping", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(lbl6, 2160, 840, 1695, 255)
        self.txt_delay2 = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_delay2, 3960, 840, 975, 285)

        lbl7 = tk.Label(frame2, text="NOT USED", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(lbl7, 2520, 1200, 1335, 255)
        self.txt_delay3 = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_delay3, 3960, 1200, 975, 285)

        lbl8 = tk.Label(
            frame2, text="Meter Delay (Keithley Param)", bg=VB_FORM_BG, font=VB_FONT, anchor="e",
            justify="right", wraplength=85,
        )
        place(lbl8, 2520, 1560, 1335, 615)
        self.txt_meter_delay = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_meter_delay, 3960, 1560, 975, 285)

        lbl9 = tk.Label(
            frame2, text="Averages for Keithley", bg=VB_FORM_BG, font=VB_FONT, anchor="e",
            justify="right", wraplength=70,
        )
        place(lbl9, 360, 1320, 1095, 495)
        self.txt_averages = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_averages, 1560, 1440, 975, 285)

        lbl10 = tk.Label(frame2, text="Iterations", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(lbl10, 360, 1800, 975, 255)
        self.txt_iterations = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_iterations, 1560, 1800, 975, 285)

        lbl11 = tk.Label(frame2, text="Meter Range", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(lbl11, 120, 2280, 1335, 255)
        self.txt_meter_range = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_meter_range, 1560, 2280, 975, 285)

        lbl12 = tk.Label(
            frame2, text="Meter Current Limit ", bg=VB_FORM_BG, font=VB_FONT, anchor="e",
            justify="right", wraplength=62,
        )
        place(lbl12, 2880, 2280, 975, 495)
        self.txt_meter_current_limit = tk.Entry(frame2, bg=VB_FIELD_BG, font=VB_FONT)
        place(self.txt_meter_current_limit, 3960, 2280, 975, 285)

    # -- behavior -------------------------------------------------------

    def _log(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_data.configure(state="normal")
        self.txt_data.insert("end", f"[{timestamp}] {text}\n")
        self.txt_data.see("end")
        self.txt_data.configure(state="disabled")

    def _form_load(self):
        """frmRunTime.Form_Load (sub_414ee0): set the status label, default log file
        name, populate comboDies, and set cmdRevert's caption for the incoming mode."""
        self.lbl_info.configure(
            text=f"Recipe: {self.recipe_name}\nWafer: {self.wafer_id}"
        )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_log_name = f"C:\\ProbeData\\{self.recipe_name}_{timestamp}.txt"
        self.txt_file_name.insert(0, default_log_name)
        self.txt_wafer_id_frame1.insert(0, self.wafer_id)

        self.combo_dies["values"] = data_stub.DEMO_COMBO_DIES
        if data_stub.DEMO_COMBO_DIES:
            self.combo_dies.current(0)

        self._update_revert_caption()

        # Form_Load's first real step: pull each instrument's GPIB address from
        # tblProberConfiguration (fldName -> "HPIB_"+fldName control, fldAddress ->
        # its .Address) - see data_stub.load_prober_configuration's docstring and
        # GPIB_COMMANDS.txt section 0. The real exe assigns .Address here; our
        # drivers already opened their (matching) address in their own constructor
        # (data_stub.build_hpib_instruments()), so this loop now just logs the same
        # status text, verbatim from the real exe's string table, one line per row.
        _init_status = {
            "2001X": "Initializing Electroglass",
            "Relay1": "Initializing Switches",
            "Keithley2400": "Initializing Keithley 2400",
        }
        for name, _address in data_stub.load_prober_configuration("LampElectrical"):
            if name not in self._hpib_by_name:
                continue
            self._log(_init_status.get(name, f"Initializing {name}"))

        # Same Form_Load loop also reads each row's fld2001XSyntax and sends it
        # (non-blank ones only) to HPIB_2001X - see data_stub.PROBER_INIT_SEQUENCE's
        # docstring and GPIB_COMMANDS.txt section 0.7 for the real DB content this
        # is sourced from. Now actually sent over GPIB (2026-07-22) - .write() is a
        # no-op if the real session failed to open (GPIBInstrument.write() checks
        # self.inst), so this is safe to run even with no hardware attached.
        for _order, instruction, comment, syntax in data_stub.PROBER_INIT_SEQUENCE:
            if not syntax:
                continue
            self._log(f"{instruction} ({comment}): {syntax}")
            self.hpib_2001x.write(syntax)

        # Then warns (Yes/No "Continue anyway?") for any that fail to configure -
        # binaryninja.txt ~line 11245. Reachability is now a real check
        # (instrument.inst is None means GPIBInstrument's pyvisa open_resource()
        # genuinely failed - see data_stub.build_hpib_instruments()'s docstring),
        # not a hardcoded always-False stub, so this behaves the same on a PC with
        # no GPIB hardware attached as it did before, but for a real reason.
        for name, instrument in (
            ("Relay1", self.hpib_relay1),
            ("2001X", self.hpib_2001x),
            ("Keithley2400", self.hpib_keithley2400),
        ):
            if instrument.inst is not None:
                continue
            self._log(f"Configure HPIB Failed: HPIB_{name}")
            proceed = messagebox.askokcancel(
                MSG_TITLE,
                f"Configure HPIB Failed\n\nHPIB_{name}: the GPIB/VISA resource "
                f"{instrument.address!r} could not be opened.\n\nContinue anyway?",
            )
            if not proceed:
                self._log("Configuration cancelled by user")
                self.cmd_go.configure(state="disabled")
                return

        self._log("Ready")

    def _update_revert_caption(self):
        # cmdRevert's caption flips depending on which mode is CURRENTLY active - it always
        # reads as an offer to switch to the *other* mode.
        if self.mode_var.get() == "Full":
            self.cmd_revert.configure(text="Change to Engineering Mode")
        else:
            self.cmd_revert.configure(text="Change to Production Mode")

    def cmd_revert_click(self):
        """cmdRevert_Click (sub_414ac0): live override toggle between Full/Manual mode,
        re-applying the Tag="View=Manual;" show/hide on Frame1/Frame2."""
        self.mode_var.set("Manual" if self.mode_var.get() == "Full" else "Full")
        self._update_revert_caption()
        self.apply_mode(self.mode_var.get())

    def cmd_view_click(self):
        """cmdView_Click (sub_414c60): open the session log file in Notepad, or complain
        if it doesn't exist yet."""
        path = self.txt_file_name.get().strip()
        if not path or not os.path.isfile(path):
            messagebox.showinfo(MSG_TITLE, f"The data file '{path}' cannot be found!")
            return
        subprocess.Popen([r"C:\Windows\Notepad.exe", path])  # hardcoded in the original too

    def cmd_go_click(self):
        """cmdGo_Click (sub_40cba0): the real handler re-validates Wafer ID, loads the
        .PMA recipe, moves the prober to the align site, confirms Z-height/edge-sensor
        state with the operator, walks every die sending switch-relay + Keithley SCPI
        commands, and finally sends the stage home. Simulated here via
        data_stub.simulated_run_steps() against a fake die list, since there's no real
        prober/GPIB/DB connected yet - see data_stub.py's module docstring."""
        if self._run_in_progress:
            return
        wafer_id = self.txt_wafer_id_frame1.get().strip()
        if not wafer_id:
            messagebox.showinfo(MSG_TITLE, "Please enter a Wafer ID")
            return

        # Non-blocking warning if there's uncollected data sitting in C:\ProbeData
        # (binaryninja.txt ~line 3802) - shown, then probing continues regardless.
        uncollected = data_stub.uncollected_data_files()
        if uncollected:
            messagebox.showinfo(
                MSG_TITLE,
                "Data files found in C:\\ProbeData that have not been collected "
                "into the database.\nYou may continue probing, but please tell an "
                "engineer or the programmer!",
            )

        # If a text log is requested, the destination folder actually has to exist -
        # VB6's Open ... For Output would raise run-time error 76 ("Path not found")
        # here rather than silently creating C:\ProbeData itself.
        if self.chk_save_text_var.get() and not os.path.isdir(data_stub.PROBE_DATA_DIR):
            messagebox.showerror(
                "Microsoft Visual Basic",
                "Run-time error '76':\n\nPath not found",
            )
            return

        self._run_in_progress = True
        self.cmd_go.configure(state="disabled")
        self._run_steps = data_stub.simulated_run_steps()
        self._advance_run()

    def _advance_run(self):
        try:
            text, is_log_line = next(self._run_steps)
        except StopIteration:
            self._run_in_progress = False
            self.cmd_go.configure(state="normal")
            return

        if is_log_line:
            self._log(text)
        else:
            self.lbl_info.configure(text=f"Recipe: {self.recipe_name}\nWafer: {self.wafer_id}\n{text}")
            self._log(text)

        if text == "Ready" and not self._align_confirmed:
            self._align_confirmed = True
            proceed = messagebox.askokcancel(
                MSG_TITLE,
                "Align of wafer complete. Click 'OK' to commence probing, or 'Cancel' as "
                "the last chance to abort.\n\n"
                "You MUST now check the 'Z' height on the prober lower key pad \n"
                "The Green light on the edge sensor box should then be on.\n"
                " Last chance to abort!",
            )
            if not proceed:
                self._log("Run cancelled by user")
                self._run_in_progress = False
                self.cmd_go.configure(state="normal")
                return

        if text == "Probe Recipe completed normally":
            messagebox.showinfo(MSG_TITLE, "Probe recipe complete!\nClick 'OK' to send probe stage home.")

        self.after(400, self._advance_run)
