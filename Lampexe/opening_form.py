import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import data_stub
from layout import ModeAwareMixin, VB_FIELD_BG, VB_FONT, VB_FONT_BOLD, VB_FORM_BG, client_size, make_frame, place

# "Software rev: " is a verbatim string recovered from Form_Load (binaryninja.txt:3001);
# what's concatenated after it at runtime reads from a lazily-created helper object
# (data_42351c) whose exact property chain wasn't confidently traced, so the version
# numbers here are filled in from Project.vbp's MajorVer=1/MinorVer=00/RevisionVer=0001.
VERSION_TEXT = "Software rev: 1.00.0001"

MSG_TITLE = "IMT LampElectrical Probing"  # the msgbox title used everywhere in the original


class OpeningForm(tk.Tk, ModeAwareMixin):
    """Recreation of frmOpening.frm - the recipe/wafer-info entry screen shown at startup."""

    def __init__(self):
        tk.Tk.__init__(self)
        ModeAwareMixin.__init__(self)

        self.title("Opening Form")  # frmOpening.Caption
        w, h = client_size(8730, 5895)  # frmOpening.ClientWidth/ClientHeight
        self.geometry(f"{w}x{h}")
        self.configure(bg=VB_FORM_BG)

        # Option1 ("Full", TabIndex 2) comes before Option2 ("Manual"/Engineering, TabIndex
        # 3) - VB6 auto-selects the lowest-TabIndex OptionButton in a group when neither has
        # an explicit Value=True in the .frm, so "Full" is the real startup default.
        self.mode_var = tk.StringVar(value="Full")
        self.suppress_debug_var = tk.BooleanVar(value=False)
        self._dots_running = False

        self._build_menu()
        self._build_controls()
        self.apply_mode(self.mode_var.get())
        self._form_load()

    # -- layout -------------------------------------------------------

    def _build_menu(self):
        # Begin VB.Menu File > SetProberName ("Set Prober Name"), ProberExit ("Exit")
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Prober Name", command=self.set_prober_name_click)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.prober_exit_click)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def _build_controls(self):
        # Label1 "LampElectrical Probing" - L480 T120 W3135 H495, 12pt bold
        lbl1 = tk.Label(
            self, text="LampElectrical Probing", bg=VB_FORM_BG, font=("MS Sans Serif", 12, "bold"), anchor="w"
        )
        place(lbl1, 480, 120, 3135, 495)

        # lblVersion "Version Number" - L3960 T120 W4215 H255, right-aligned
        self.lbl_version = tk.Label(self, text=VERSION_TEXT, bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        place(self.lbl_version, 3960, 120, 4215, 255)

        # Label5/6/7 - bold 8.25pt instructional text, always visible (no Tag)
        lbl5 = tk.Label(
            self,
            text="Load the wafer and conduct the pre-alignment",
            bg=VB_FORM_BG,
            font=VB_FONT_BOLD,
            anchor="w",
            justify="left",
            wraplength=225,
        )
        place(lbl5, 120, 720, 3375, 495)

        lbl7 = tk.Label(
            self,
            text="Make sure the prober is Online (yellow On Line Key) - display says 'X I/O...ONLINE'",
            bg=VB_FORM_BG,
            font=VB_FONT_BOLD,
            anchor="w",
            justify="left",
            wraplength=240,
        )
        place(lbl7, 120, 1320, 3735, 495)

        lbl6 = tk.Label(
            self, text="Click the GO button below", bg=VB_FORM_BG, font=VB_FONT_BOLD, anchor="w"
        )
        place(lbl6, 120, 1920, 3375, 375)

        # lblHotWire - 13.5(->14)pt regular warning banner
        lbl_hotwire = tk.Label(
            self,
            text="NOT FOR PRODUCTION: This is a hot wired debug version only",
            bg=VB_FORM_BG,
            font=("MS Sans Serif", 14),
            anchor="w",
            justify="left",
            wraplength=310,
        )
        place(lbl_hotwire, 3720, 2520, 4695, 735)

        # Frame1 "Operational Mode" with the two run-mode OptionButtons inside it.
        frame1 = make_frame(self, "Operational Mode", 3840, 720, 4335, 1695)
        opt1 = tk.Radiobutton(
            frame1,
            text="Run a full production probe with data collection",
            variable=self.mode_var,
            value="Full",
            bg=VB_FORM_BG,
            font=VB_FONT_BOLD,
            anchor="w",
            justify="left",
            wraplength=230,
            command=self._on_mode_changed,
        )
        place(opt1, 240, 360, 3855, 375)
        opt2 = tk.Radiobutton(
            frame1,
            text="Engineering Mode with display and quick data logging only",
            variable=self.mode_var,
            value="Manual",
            bg=VB_FORM_BG,
            font=VB_FONT_BOLD,
            anchor="w",
            justify="left",
            wraplength=225,
            command=self._on_mode_changed,
        )
        place(opt2, 240, 840, 3735, 615)

        # cmdGo "GO" - L360 T2760 W1215 H495
        self.cmd_go = tk.Button(self, text="GO", font=VB_FONT_BOLD, command=self.cmd_go_click)
        place(self.cmd_go, 360, 2760, 1215, 495)

        # chkSuppressDebug - L240 T3840 W2775 H255
        chk = tk.Checkbutton(
            self,
            text="Suppress Debug Messages",
            variable=self.suppress_debug_var,
            bg=VB_FORM_BG,
            font=VB_FONT,
            anchor="w",
        )
        place(chk, 240, 3840, 2775, 255)

        # Operator ID / Process Step / Wafer ID labels+fields - Tag="View=Full;" in the
        # original (production mode only; Engineering Mode hides these, matching Option2's
        # caption "...display and quick data logging only" with no per-wafer bookkeeping).
        lbl_operator = tk.Label(self, text="Operator ID", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        self.register_view_tag(lbl_operator, "Full", 3360, 3480, 1215, 255)

        self.txt_operator_id = tk.Entry(self, bg=VB_FIELD_BG, font=VB_FONT)
        self.txt_operator_id.insert(0, "Operator Name")
        self.register_view_tag(self.txt_operator_id, "Full", 4680, 3480, 3015, 285)

        lbl_process = tk.Label(self, text="Process Step", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        self.register_view_tag(lbl_process, "Full", 3360, 4440, 1215, 255)

        self.txt_process_step = tk.Entry(self, bg=VB_FIELD_BG, font=VB_FONT)
        self.txt_process_step.insert(0, "The Process Step")
        self.register_view_tag(self.txt_process_step, "Full", 4680, 4440, 3015, 285)

        lbl_wafer = tk.Label(self, text="Wafer ID", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        self.register_view_tag(lbl_wafer, "Full", 3360, 3960, 1215, 255)

        self.txt_wafer_id = tk.Entry(self, bg=VB_FIELD_BG, font=VB_FONT)
        self.txt_wafer_id.insert(0, "The Wafer ID")
        self.register_view_tag(self.txt_wafer_id, "Full", 4680, 3960, 3015, 285)

        lbl_recipes = tk.Label(self, text="Recipes Available", bg=VB_FORM_BG, font=VB_FONT, anchor="e")
        self.register_view_tag(lbl_recipes, "Full", 840, 4920, 2055, 255)

        # comboRecipes - L3240 T4920 W5175 H315 (not Tag'd in the original; the picker stays
        # present in both modes even though its label is Full-only, so mirror that exactly).
        self.combo_recipes = ttk.Combobox(self, font=VB_FONT, state="readonly")
        place(self.combo_recipes, 3240, 4920, 5175, 315)

        # lblInfo - status line, blank at design time
        self.lbl_info = tk.Label(self, text="", bg=VB_FORM_BG, font=VB_FONT, anchor="w")
        place(self.lbl_info, 240, 5400, 8415, 375)

        # Timer1 has no screen presence; see the module docstring note below for why it's
        # left inert rather than guessed at.

    def _on_mode_changed(self):
        self.apply_mode(self.mode_var.get())

    # -- behavior -------------------------------------------------------

    def _timer1_tick(self):
        """
        Timer1_Timer (sub_40c7e0), resolved by hand-tracing the raw disassembly in
        disassembledlamp/frmOpening.frm (2026-07-22) - none of the 4 decompiler
        outputs surfaced this on their own. The literal string at data_405ab4 turned
        out to be "." (VB Decompiler annotates it inline: `push 00405AB4h ; "."`).
        Full trace: Me.[vtable+0x32C] is fetched twice with no state change between
        the calls (so both refer to the same object), its own getter at +0x50 is
        read into a temp, and "." & temp is written back via the setter at +0x54.
        That exact +0x32C/+0x54 getter/setter pair is ALSO used in cmdGo_Click to
        set the caption "Loading Run Time Form, please wait" - which pins +0x32C
        down as lblInfo specifically (the form's one status-message label), not an
        ambiguous target. So: every tick, lblInfo grows another "." appended to
        its own caption - a classic "please wait / working" animation.

        The real Interval/Enabled values weren't confirmed (Timer1 has no explicit
        Enabled=False or Interval=N in the .frm, and VB6 Timers default to
        Interval=0, which never fires - so something must set it at runtime,
        unconfirmed where). 500ms and capping the dot run at 10 are reasonable
        choices to make the animation visible without becoming unbounded, not
        recovered values.
        """
        if not self._dots_running:
            return
        current = self.lbl_info.cget("text")
        dots = current.count(".") if set(current) <= {"."} else 0
        self.lbl_info.configure(text="." * ((dots + 1) % 11 or 1))
        self.after(500, self._timer1_tick)

    def _start_dots(self):
        self._dots_running = True
        self.lbl_info.configure(text="")
        self._timer1_tick()

    def _stop_dots(self):
        self._dots_running = False
        self.lbl_info.configure(text="")

    def _form_load(self):
        """frmOpening.Form_Load (sub_40b650): populate comboRecipes from the recipe folder."""
        recipes = data_stub.scan_recipes()
        self.combo_recipes["values"] = recipes
        if recipes:
            self.combo_recipes.current(0)

    def cmd_go_click(self):
        """cmdGo_Click (sub_40ae20): validate Wafer ID + recipe selection, then hand off
        to the Run Time form."""
        wafer_id = self.txt_wafer_id.get().strip()
        if self.mode_var.get() == "Full" and wafer_id in ("", "The Wafer ID"):
            messagebox.showinfo(MSG_TITLE, "Please enter the Wafer ID.")
            return

        # Operator ID / Process Step are required too (binaryninja.txt ~lines 2509-2599):
        # each is checked against its own default-placeholder text and against empty,
        # same pattern as Wafer ID above. (There's also a "Tell an Engineer!" branch,
        # reached only when BOTH already look filled in, that wasn't confidently traced -
        # left unimplemented rather than guessed at; it doesn't gate the normal
        # fill-in-the-fields case these two messages cover.)
        if self.mode_var.get() == "Full":
            operator_check = self.txt_operator_id.get().strip()
            if operator_check in ("", "Operator Name"):
                messagebox.showinfo(MSG_TITLE, "Please enter your Operator ID.")
                return
            process_check = self.txt_process_step.get().strip()
            if process_check in ("", "The Process Step"):
                messagebox.showinfo(MSG_TITLE, "Please enter the Process Step.")
                return

        recipe = self.combo_recipes.get()
        if not recipe:
            # Resolved 2026-07-22 from the actual exe's raw string table (byte offsets
            # 21732/21812, immediately after "Please enter the Process Step." in the
            # binary): "Tell an Engineer!" is the msgbox TITLE for this message, not a
            # separate branch - an earlier reading of the decompiled HLIL had this
            # backwards (looked like a condition reached only when both fields were
            # already filled in, which never made sense; a plain read of the raw string
            # order settles it correctly).
            messagebox.showinfo(
                "Tell an Engineer!",
                "This file is needed, even in Engineering Mode, to establish the die moves.",
            )
            return

        # Re-validate the recipe's .PMA AND its 6 .PMV/.PMS siblings are still there
        # (matches the original's own re-check + "ERROR is not a valid recipe name!"/
        # "Not found " messages) - comboRecipes is only ever populated from a real
        # directory scan, but files could still have been deleted since Form_Load.
        missing = data_stub.missing_recipe_files(recipe)
        if missing:
            missing_names = "\n".join(os.path.basename(p) for p in missing)
            messagebox.showinfo(
                MSG_TITLE,
                f"ERROR is not a valid recipe name!\nThis is caused by the system not "
                f"locating the following file(s) in {data_stub.REAL_RECIPE_DIR}:\n"
                f"{missing_names}",
            )
            self.combo_recipes.set("")
            self._form_load()
            return

        operator_id = self.txt_operator_id.get().strip() if self.mode_var.get() == "Full" else ""
        process_step = self.txt_process_step.get().strip() if self.mode_var.get() == "Full" else ""

        # Timer1's dots animation onto lblInfo (see _timer1_tick's docstring) shares its
        # getter/setter pair with the confirmed "Loading Run Time Form, please wait"
        # caption set in this same real handler right before frmRunTime is shown - so
        # this is where it plausibly starts: status text updates don't need frmRunTime
        # to actually exist yet, unlike the OCX-triggered crash below, which is why
        # that check happens AFTER this, inside _go_to_runtime, not before it.
        self._start_dots()
        self.after(
            1200,
            lambda: self._go_to_runtime(recipe, wafer_id, operator_id, process_step),
        )

    def _go_to_runtime(self, recipe, wafer_id, operator_id, process_step):
        self._stop_dots()

        # VB6 creates every control on a form - including its ActiveX controls - when
        # the form itself is instantiated. The real frmRunTime has 3 Agt3494ALib.
        # Agt3494A instances, and would crash here with run-time error 339 on any PC
        # missing AGT3494A.OCX (true almost everywhere - it's Agilent's discontinued,
        # Windows-XP-era IntuiLink control). Lampexe doesn't reproduce that crash
        # (2026-07-22): it's a ground-up Python rewrite that talks GPIB via pyvisa
        # directly (RuntimeForm's HPIB_* instruments, see
        # data_stub.build_hpib_instruments()), so it was never actually dependent on
        # that OCX - simulating its specific failure mode stopped being a meaningful
        # fidelity target once real hardware communication became the point.
        from runtime_form import RuntimeForm

        self.withdraw()
        run_form = RuntimeForm(
            self,
            recipe_name=recipe,
            wafer_id=wafer_id or "N/A",
            operator_id=operator_id or data_stub.get_prober_name(),
            process_step=process_step,
            mode=self.mode_var.get(),
        )
        run_form.protocol("WM_DELETE_WINDOW", lambda: (run_form.destroy(), self.destroy()))

    def set_prober_name_click(self):
        """SetProberName_Click: InputBox to rename this prober, persisted via
        (stubbed) SaveSetting/GetSetting under IMTProber/Names/ProberName."""
        current = data_stub.get_prober_name()
        new_name = simpledialog.askstring(
            "Prober Name",
            "Enter a new name for this prober so as to identify its data in the database.",
            initialvalue=current,
            parent=self,
        )
        if new_name:
            data_stub.set_prober_name(new_name)
            messagebox.showinfo(MSG_TITLE, f"Prober Name '{new_name}' saved.")

    def prober_exit_click(self):
        self.destroy()
