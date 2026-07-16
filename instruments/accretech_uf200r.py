import time
from instruments.gpib_base import GPIBInstrument

# Default STB code table (UF200/190 GP-IB manual, doc FT02000-R003-E0).
# NOTE: All STB codes are USER-CONFIGURABLE on the prober (STB Code Settings
# menu). The values below are the factory defaults. If your installation has
# changed them, update the _wait_for_stb() calls to match.
STB_DESCRIPTIONS = {
    64:  "GP-IB Initial Setting Done",
    65:  "Absolute Value Travel Done (A cmd) — Chuck DOWN at end",
    66:  "Coordinate Travel Done — Chuck DOWN at end (J/S/C/M)",
    67:  "Z UP / Test Start — Chuck UP at end (Z/A/G/J/M/P/S) — wafer in CONTACT with probe card",
    68:  "Z DOWN done (D cmd) — wafer separated from probe card",
    69:  "Marking Done (C/M cmd)",
    70:  "Wafer Loading Done (G/L/N/j2 cmd) — start die positioned, Chuck DOWN",
    71:  "Wafer Unloading Done (U/U0/U9)",
    74:  "Out of Probing Area — X/Y/Z unchanged (A/J/S/js cmd)",
    75:  "Prober Initial Setting Done",
    76:  "Error — check alarm screen",
    77:  "Index Setting Done (I cmd)",
    78:  "Pass Counting Up Done (P cmd)",
    79:  "Fail Counting Up Done (F cmd)",
    80:  "Wafer Count — output at unloading wafer",
    81:  "Wafer End — all dice or sample dice complete",
    82:  "Cassette End",
    84:  "Alignment Rejection Error (j2)",
    85:  "Stop Command Received (K cmd)",
    86:  "Print Data Receiving Done (p cmd)",
    87:  "Warning Error — prober continues working",
    88:  "Test Start (Count Not Needed) — Fail check-back, Chuck UP, result not counted",
    89:  "Needle Cleaning Done (W/jc cmd)",
    90:  "Probing Stop — intended stop, yield NG, or stop on start die",
    91:  "Probing Restart from stop condition",
    92:  "Z Up/Down Fine Adjustment Done (Z± cmd)",
    93:  "Hot Chuck Temp Command Received (h cmd)",
    94:  "Lot Done (jv cmd)",
    98:  "Command Normally Done",
    99:  "Command Abnormally Done / Data Error",
    100: "Test Done received from Tester",
    101: "Alarm Buzzer ON (em cmd)",
    103: "Map Data Download Normally Done",
    104: "Map Data Download Abnormally Done",
    105: "Able to Adjust Needle Height",
    107: "Binary Data Upload Start (du cmd)",
    108: "Binary Data Upload Finish (du cmd)",
    109: "j2 Command Receive OK",
    110: "Needle/Fail Mark OK (jp/jm cmd)",
    111: "Needle/Fail Mark NG (jp/jm cmd)",
    113: "Re-Alignment Done (N1 cmd)",
    114: "Auto Needle Alignment Normally Done (N2 cmd)",
    115: "Auto Needle Alignment Abnormally Done (N2 cmd)",
    116: "Chuck Height Setting Done (z cmd)",
    117: "Continuous Fail Error (custom STB change required)",
    118: "Wafer Loading Done without alignment (L1/L9 cmd)",
    119: "Error Recovery Done / Wafer Centering Complete (es/N9 cmd)",
    120: "Prober Start Normally Done (st cmd)",
    121: "Prober Start Abnormally Done (st cmd)",
    122: "Probe-mark Inspection Finish (np cmd)",
    123: "Fail-mark Inspection Finish (fp cmd)",
}


class AccretechUF200R(GPIBInstrument):
    def __init__(self):
        super().__init__('prober')
        # Chuck Z state is NOT queryable on the prober — the only Z information
        # is the completion STB of each motion command, so it is tracked here.
        # True = chuck UP (wafer in CONTACT with probe card), False = chuck
        # DOWN (separated), None = unknown (no reply seen yet, or error).
        self.z_is_up = None
        if self.inst:
            self.inst.timeout = 30000
            self.inst.write_termination = '\r\n'
            self.inst.read_termination  = '\r\n'

    # ── Safe read commands (no motion, always permitted) ─────────────────────

    def get_prober_id(self) -> str:
        """B — Request prober ID / user-defined label. Always safe."""
        return self.query("B") or ""

    def get_error_code(self) -> str:
        """E — Short error code string. Call when STB=76."""
        return self.query("E") or ""

    def get_error_message(self) -> str:
        """e — Full error message text. More detail than E."""
        return self.query("e") or ""

    def get_prober_status(self) -> str:
        """ms — Prober status code string."""
        return self.query("ms") or ""

    def get_xy_position(self) -> str:
        """Q — Current DIE coordinates (§4.24). Response "QY<3>X<3>",
        die map units -99…511 (clips at -99), Y before X.
        Only meaningful during probing — response is indefinite otherwise."""
        return self.query("Q") or ""

    def get_xy_absolute(self) -> str:
        """R — Current absolute coordinates in the probing area (§4.25).
        Response "RY<7>X<7>" in 0.1 µm (or 10⁻⁵ inch) units, Y before X.
        Probing-only — command error otherwise."""
        return self.query("R") or ""

    def get_on_wafer_info(self) -> str:
        """O — On-wafer information (current die). Only valid during probing."""
        return self.query("O") or ""

    def get_lot_number(self) -> str:
        """V — Current lot number."""
        return self.query("V") or ""

    def get_wafer_number(self) -> str:
        """X — Current wafer number in lot."""
        return self.query("X") or ""

    def get_wafer_id(self) -> str:
        """b — Wafer ID (interchangeable with W for ID depending on config)."""
        return self.query("b") or ""

    def get_pass_fail_counts(self) -> str:
        """c — Pass and Fail counts for the current wafer."""
        return self.query("c") or ""

    def get_gross_value(self) -> str:
        """Y — Gross die count."""
        return self.query("Y") or ""

    def get_wafer_status(self) -> str:
        """w — Wafer processing status in cassette slots."""
        return self.query("w") or ""

    def get_cassette_status(self) -> str:
        """x — Cassette slot occupancy status."""
        return self.query("x") or ""

    def get_yield_data(self) -> str:
        """y — Yield data for current lot."""
        return self.query("y") or ""

    def get_hot_chuck_status(self) -> str:
        """r — Hot-chuck temperature status."""
        return self.query("r") or ""

    def get_chuck_temperature(self) -> str:
        """f — Chuck temperature reading."""
        return self.query("f") or ""

    def get_start_die_coords(self) -> str:
        """q — Start die (first die) XY coordinates."""
        return self.query("q") or ""

    def get_multisite_info(self) -> str:
        """H — Multi-site location number info."""
        return self.query("H") or ""

    def buzzer_clear(self) -> str:
        """Buzzer Clear: E then es (§4.5 + §4.47).

        E reads the pending error code (outputs nothing when no error state),
        then es requests error clearance — clears the alarm / silences the
        buzzer. STB=119 (Error Recovery Done) confirms. Returns the error
        code read, "" if none was pending.
        """
        code = ""
        if not self.inst:
            return code
        old_timeout = self.inst.timeout
        try:
            self.inst.timeout = 3000   # E stays silent when no error is pending
            code = (self.query("E") or "").strip()
        except Exception:
            pass
        finally:
            self.inst.timeout = old_timeout
        self.write("es")
        # Wait for STB=119; tolerate 76 still being reported while the
        # clearance is in progress (do NOT raise like _wait_for_stb would).
        start = time.time()
        while time.time() - start < 5.0:
            try:
                if self.inst.read_stb() == 119:
                    break
            except Exception:
                break
            time.sleep(0.05)
        return code

    def send_es(self):
        """es — clear the alarm buzzer signal only, with no E read first and
        no wait for an STB=119 confirmation (see buzzer_clear() for that
        fuller E+es+confirm sequence). Used for the lightweight, fire-and-
        forget auto-clear on a known benign error code (see
        _maybe_auto_clear_buzzer) and by every Abort/Stop Run action."""
        self.write("es")

    def _maybe_auto_clear_buzzer(self):
        """Called right after a GENUINE (confirmed) STB=76 alarm, before it
        is raised as an error. Reads the pending error code (E) and, for
        known benign codes — currently EO0691, a GP-IB command sent while
        the prober wasn't in the right state to accept it — automatically
        sends es to silence the buzzer on the operator's behalf. Best-
        effort only: any failure here is swallowed so it can never mask
        the real alarm the caller is about to raise."""
        if not self.inst:
            return
        try:
            old_timeout = self.inst.timeout
            try:
                self.inst.timeout = 3000   # E stays silent when no error is pending
                code = (self.query("E") or "").strip()
            finally:
                self.inst.timeout = old_timeout
            if "0691" in code:
                self.send_es()
        except Exception:
            pass

    def confirm_and_clear_alarm(self) -> bool:
        """Background-watcher entry point (see AtomicaDashboard.
        _poll_prober_ready): given an already-observed STB=76, confirm it
        is a real, sustained alarm — not a transient serial-poll misread,
        same debounce as _confirm_alarm — and if so send es to clear the
        buzzer UNCONDITIONALLY, regardless of the specific error code
        (unlike _maybe_auto_clear_buzzer, which only auto-clears a single
        known benign code and only fires inline while a command is
        actively being waited on). Intended to run only while idle (no
        run in progress) so a genuine alarm during a run still surfaces
        normally rather than being silently swallowed. Returns True if es
        was sent."""
        if not self.inst:
            return False
        try:
            if self._confirm_alarm() == 76:
                self.send_es()
                return True
        except Exception:
            pass
        return False

    def read_stb_decoded(self) -> tuple:
        """Read the GPIB status byte and return (int_value, description)."""
        if not self.inst:
            return 0, "Not connected"
        stb = self.inst.read_stb()
        desc = STB_DESCRIPTIONS.get(stb, f"Unknown STB code")
        return stb, desc

    # ── Chuck Z motion (probing-only) ─────────────────────────────────────────
    #
    # On the UF200/190 the CHUCK (carrying the wafer) moves in Z, not the
    # probe card:
    #   Z (Z UP)   — chuck rises to Probing Height INCLUDING OVERDRIVE:
    #                the wafer CONTACTS the probe card needles. NOT a safe lift.
    #   D (Z DOWN) — chuck drops away from the probe card: the wafer SEPARATES
    #                from the needles. This is the safe direction.
    # Manual flowcharts (§4.36 / §4.4) show both are rejected with a command
    # error unless probing is active (start die positioned → last die tested).

    def z_up(self):
        """Z — Drive CHUCK UP to Probing Height including overdrive (§4.36).

        ⚠ CONTACT: the wafer touches the probe card needles.
        Probing-only. STB=67 when done — returned so the caller can confirm
        it explicitly rather than just trusting "no exception was raised".
        """
        self.write("Z")
        return self._wait_motion_stb({67})

    def z_down(self):
        """D — Drive chuck DOWN, separating wafer from the probe card (§4.4).

        Safe direction (breaks needle contact). Probing-only. STB=68 when
        done — returned so the caller can confirm it explicitly.
        """
        self.write("D")
        return self._wait_motion_stb({68})

    def emergency_stop(self):
        """K — Stop prober operation (§4.12). STB=85 confirms stop received.

        K can interrupt a motion mid-travel, so the tracked Z state becomes
        unknown — send D (separate) to re-establish a known height.
        """
        self.write("K")
        self._wait_for_stb(target_stb=85)
        self.z_is_up = None

    def unload_wafer(self):
        """U — Unload the current wafer from the chuck back to the
        cassette. STB=71 confirms unloading done. The wafer is no longer
        on the chuck afterward, so the tracked Z-contact state becomes
        inapplicable (same treatment as emergency_stop)."""
        self.write("U")
        stb = self._wait_for_stb_any({71})
        self.z_is_up = None
        return stb

    # ── Cassette automation workflow (see gui/cassette_panel.py) ─────────────
    #
    # A SEPARATE, higher-level workflow from the G/Z/D/J die-walk commands
    # above. The operator loads a cassette via the touchscreen (EOI
    # §8.4.1-8.4.10); the prober then automatically pulls a wafer, aligns
    # it, and drives the chuck into contact with Die #1 — broadcasting
    # STB=65 the instant it does. From there:
    #   J (Next Die)  -> ignore STB=100 (Moving) while polling; STB=66 =
    #                    arrived at the next die; STB=67 = end of wafer
    #                    map (no more dies on this wafer — J does not
    #                    move the chuck).
    #   U (Unload/Load Next) -> sent after STB=67; the prober racks the
    #                    finished wafer, pulls the next one from the
    #                    cassette, aligns it, and touches Die #1 again
    #                    (another STB=65). If the cassette is now empty,
    #                    the prober goes idle (STB=0, "DONE !!" on the
    #                    touchscreen) instead of sending 65.
    #
    # IMPORTANT: this installation's STB meanings for the CASSETTE
    # workflow (65 = wafer/die-1 ready, 66 = next die arrived, 67 = end
    # of wafer map, 100 = moving, 0 = idle/lot complete) are configured
    # specifically for this workflow and are handled entirely separately
    # from the G/Z/D/J die-walk STB semantics used elsewhere in this file
    # (there, 65/66/67/68/70/81/90 mean different things — e.g. 67 there
    # means chuck-up/contact). The two call paths must never be mixed.
    #
    # These wrap the same low-level STB-polling helpers the die-walk
    # commands use (so a genuine STB=76 alarm is still confirmed/handled
    # identically either way) — only the target/ignored codes differ.

    def cassette_wait_for_wafer_ready(self, timeout_s=None):
        """Poll for STB=65 — wafer loaded, needles in contact with Die #1
        (cassette workflow). Returns 65 on success, or None on timeout
        (does not raise — a timeout here just means no wafer showed up
        yet, not necessarily an error)."""
        try:
            return self._wait_for_stb_any({65}, timeout_s)
        except TimeoutError:
            return None

    def cassette_next_die(self, timeout_s=None):
        """J — Next Die (cassette-workflow polling: STB=100/Moving is
        transparently ignored while waiting, same as any other STB not
        in the target set). Returns 66 (next die arrived) or 67 (end of
        wafer map — chuck did not move), or None on timeout."""
        self.write("J")
        try:
            return self._wait_for_stb_any({66, 67}, timeout_s)
        except TimeoutError:
            return None

    def cassette_unload_and_load_next(self, timeout_s=None):
        """U — Unload the finished wafer and load the next one from the
        cassette (cassette-workflow semantics — distinct from
        unload_wafer()'s plain single-wafer-out U/STB=71). Returns 65 if
        the next wafer reaches Die #1 contact, or None if the cassette is
        now empty (prober goes idle / STB=0) or the wait simply times
        out."""
        self.write("U")
        try:
            stb = self._wait_for_stb_any({65, 0}, timeout_s)
        except TimeoutError:
            return None
        return stb if stb == 65 else None

    # ── Motion (probing sequence) ─────────────────────────────────────────────
    #
    # All XY travel commands (A/G/J/S) drop the chuck to Z-DOWN for the travel
    # and then RETURN it to the height it had before the command — if the wafer
    # was in contact before the move, it RE-CONTACTS at the new position.
    # Send D first if contact after the move is not wanted.

    def next_die(self):
        """J — Position the next testing die (§4.11).

        STB=66 (finish chuck DOWN) / 67 (finish chuck UP) / 81 (wafer end).
        STB=90 if <STOP> was pushed on the prober: chuck stays down and the
        prober waits for its START switch. Returns the STB seen.
        """
        self.write("J")
        return self._wait_motion_stb({66, 67, 81, 90})

    def set_index_size(self, x_um: float, y_um: float):
        """I — Index (die pitch) setting:  I Y<5 digits> X<5 digits>  (§4.10).

        Unit is 1 µm (10⁰ µm), unsigned, zero-padded to 5 digits, Y before X:
        e.g. X=4500 µm, Y=3200 µm → "IY03200X04500".
        Only accepted while waiting for lot process start (command error
        otherwise), and wafer + probe-pad alignment must be redone after it.
        STB=77 confirms.
        """
        xi, yi = int(round(x_um)), int(round(y_um))
        if not (0 <= xi <= 99999 and 0 <= yi <= 99999):
            raise ValueError("I: index sizes must be 0–99999 µm")
        self.write(f"IY{yi:05d}X{xi:05d}")
        self._wait_for_stb(target_stb=77)

    def move_xy_absolute(self, dx_um: float, dy_um: float):
        """A — XY travel (absolute distance):  A Y±<6 digits> X±<6 digits>  (§4.1).

        Travels BY (dx, dy) µm from the current position — "absolute distance"
        means the amount is in absolute units (1 µm per count), not that the
        target is an absolute position. X+ is leftward, Y+ is backward.
        Chuck height is restored after the travel (re-contacts if it was up).
        Probing-only. STB=65 (finish chuck DOWN) / 67 (finish chuck UP);
        STB=74 = target outside probing area, no motion.
        """
        xi, yi = int(round(dx_um)), int(round(dy_um))
        if not (-999999 <= xi <= 999999 and -999999 <= yi <= 999999):
            raise ValueError("A: travel distance must be within ±999999 µm")
        self.write(f"AY{yi:+07d}X{xi:+07d}")
        stb = self._wait_motion_stb({65, 67, 74})
        if stb == 74:
            raise RuntimeError("A: target outside probing area (STB=74) — chuck did not move")
        return stb

    def move_to_start_die(self):
        """G — Position the start die (§4.8). Used for re-testing: also resets
        the PASS/FAIL counters. Chuck height restored after the travel.
        Probing-only. STB=70 (finish chuck DOWN) / 67 (finish chuck UP).
        """
        self.write("G")
        return self._wait_motion_stb({67, 70})

    def move_to_die_xy(self, x_die: int, y_die: int):
        """J (string) — Position a target die:  J Y<3 chars> X<3 chars>  (§4.11).

        Coordinates are DIE indices in the wafer map (-99 to 511), not µm.
        Chuck height restored after the travel. Probing-only.
        STB=66/67 done; 74 = outside probing area (no motion); 81 = wafer end
        (the requested die isn't part of the prober's own loaded program —
        chuck did NOT move there); 90 = <STOP> pushed on the prober. 90 was
        missing from the wait-set here (unlike next_die()) — without it a
        genuine operator stop would silently time out instead of being
        reported immediately.
        """
        xi, yi = int(x_die), int(y_die)
        if not (-99 <= xi <= 511 and -99 <= yi <= 511):
            raise ValueError("J: die coordinates must be within -99…511")
        self.write(f"JY{yi:03d}X{xi:03d}")
        stb = self._wait_motion_stb({66, 67, 74, 81, 90})
        if stb == 74:
            raise RuntimeError("J: target die outside probing area (STB=74) — chuck did not move")
        return stb

    def move_xy_relative(self, dx_index: int, dy_index: int):
        """S — XY travel (by relative coordinates):  S Y±<4> X±<4>  (§4.26).

        Units are DIE INDEXES (whole dies, ±9999), not µm — the chuck travels
        by the demanded number of indexes along the preset coordinate
        directions. Chuck height restored after the travel. Probing-only.
        STB=66 (finish chuck DOWN) / 67 (finish chuck UP); 74 = out of area.

        Note: manual FT02000-R003-E0 §4.26 shows ±3 digits per axis, but this
        installation's UF200R expects one more digit (sign + 4 digits).
        """
        xi, yi = int(dx_index), int(dy_index)
        if not (-9999 <= xi <= 9999 and -9999 <= yi <= 9999):
            raise ValueError("S: relative travel must be within ±9999 die indexes")
        self.write(f"SY{yi:+05d}X{xi:+05d}")
        stb = self._wait_motion_stb({66, 67, 74})
        if stb == 74:
            raise RuntimeError("S: target outside probing area (STB=74) — chuck did not move")
        return stb

    def mark_current_die(self, category: str = ""):
        """C — Mark current die (format identical to M, §4.3/§4.17).
        STB=66/67 (travel done), 69 (marking done), 80/81 (wafer count/end).
        """
        cmd = f"C{category}" if category else "C"
        self.write(cmd)
        return self._wait_motion_stb({66, 67, 69, 80, 81})

    # ── Internal ─────────────────────────────────────────────────────────────

    def _wait_motion_stb(self, target_stbs: set, timeout_s: float = None) -> int:
        """Wait for a motion-completion STB and update the tracked Z state.

        Completion STBs encode the final chuck height:
          67                  → chuck UP (wafer in contact)
          65 / 66 / 68 / 70 / 90 → chuck DOWN (separated)
          74                  → out of probing area, X/Y/Z unchanged (keep state)
          69                  → marking done, height depends on marker config (unknown)
        On alarm (STB=76) or timeout the height becomes unknown (None).
        """
        try:
            stb = self._wait_for_stb_any(target_stbs, timeout_s)
        except Exception:
            self.z_is_up = None
            raise
        if stb == 67:
            self.z_is_up = True
        elif stb in (65, 66, 68, 70, 90):
            self.z_is_up = False
        elif stb == 69:
            self.z_is_up = None
        return stb

    def _confirm_alarm(self) -> int:
        """A single STB=76 read can be a transient misread — in practice
        the physical motion (Z up/down, etc.) completes fine while a stray
        poll catches 76 for one sample. Wait a beat and read again: a real,
        sustained alarm still reads 76; a spurious one clears. Returns the
        confirmation STB (may equal the caller's target)."""
        time.sleep(0.1)
        return self.inst.read_stb()

    def _wait_for_stb_any(self, target_stbs: set, timeout_s: float = None) -> int:
        """Poll STB until any code in target_stbs is seen. Returns the matched code."""
        if not self.inst:
            return 0
        timeout_seconds = timeout_s if timeout_s is not None else self.inst.timeout / 1000.0
        start_time = time.time()
        while (time.time() - start_time) < timeout_seconds:
            try:
                stb = self.inst.read_stb()
                if stb in target_stbs:
                    return stb
                if stb == 76:
                    confirm = self._confirm_alarm()
                    if confirm in target_stbs:
                        return confirm
                    if confirm == 76:
                        self._maybe_auto_clear_buzzer()
                        raise RuntimeError("PROBER HARDWARE ERROR: STB=76 (Check alarm screen)")
                    continue   # confirmed not a real alarm — keep polling
                time.sleep(0.05)
            except Exception as e:
                print(f"[PROBER] Error reading STB: {e}")
                raise
        raise TimeoutError(f"Prober timed out waiting for STB in {target_stbs}")

    def _wait_for_stb(self, target_stb: int, timeout_s: float = None):
        if not self.inst:
            return False
        timeout_seconds = timeout_s if timeout_s is not None else self.inst.timeout / 1000.0
        start_time = time.time()
        while (time.time() - start_time) < timeout_seconds:
            try:
                current_stb = self.inst.read_stb()
                if current_stb == target_stb:
                    return True
                if current_stb == 76:
                    confirm = self._confirm_alarm()
                    if confirm == target_stb:
                        return True
                    if confirm == 76:
                        self._maybe_auto_clear_buzzer()
                        raise RuntimeError("PROBER HARDWARE ERROR: STB=76 (Check alarm screen)")
                    continue   # confirmed not a real alarm — keep polling
                time.sleep(0.05)
            except Exception as e:
                print(f"[PROBER] Error reading STB: {e}")
                raise
        raise TimeoutError(f"Prober timed out waiting for STB {target_stb}")