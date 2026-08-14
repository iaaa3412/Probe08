import json
import os
import sys
import winreg

# ---------------------------------------------------------------------------
# This module stands in for everything the real prjLampElectrical.exe reached
# out to the OS/network for: two Access databases opened over ADODB
# (P:\ProberMaster.mdb, P:\LampElectricalProbeData.mdb - see basGlobalProbing's
# sub_41e8a0 in binaryninja.txt), the Windows registry (SaveSetting/GetSetting
# under "IMTProber"), a hardcoded recipe folder, and three Agt3494A GPIB/HPIB
# ActiveX controls talking to real prober/relay/SMU hardware.
#
# DB/registry/recipe access are still stand-ins (see the individual functions
# below). GPIB is NOT a stand-in anymore (2026-07-22): AGT3494A.OCX is
# Agilent's discontinued, Windows-XP-era IntuiLink ActiveX control - Lampexe
# never actually needed it (it was only ever simulated here for crash-fidelity
# with the original exe, see opening_form.py's git history / this module's old
# is_agt3494a_registered()), and this project already has real pyvisa-backed
# drivers for all 3 instruments in instruments/ (used by gui/app.py for the
# same Electroglas-flavored hardware), with instruments.yaml addresses that
# match the real DB-sourced ones below exactly. build_hpib_instruments()
# wires those in directly - see its docstring.
# ---------------------------------------------------------------------------

# instruments/ lives at the project root, one level up from this Lampexe/
# folder - add it to sys.path the same way gui/app.py does, so the imports
# below resolve regardless of Lampexe's own working directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from instruments.electroglas_2001x import Electroglas2001X
from instruments.keithley2400 import Keithley2400
from instruments.hp_switchbox import HPSwitchbox, bench_wiring

REAL_RECIPE_DIR = r"C:\ProbeRecipe\LampElectrical"

_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "_settings_stub.json")

DEFAULT_PROBER_NAME = "IMTPRB02"  # literal default baked into SetProberName_Click

# The two Jet/ADO databases opened at Sub Main, before frmOpening ever shows (see
# basGlobalProbing's sub_41e8a0 in binaryninja.txt: literal connection strings
# "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=P:\ProberMaster.mdb;..." and
# "...P:\LampElectricalProbeData.mdb;..."). There's no real Jet/ADO connection here
# (no pyodbc/pywin32 dependency in this project, and the Access driver isn't
# guaranteed installed anyway) - checking that the target file exists is the
# faithful, dependency-free proxy for "would ADODB.Connection.Open succeed": if
# the file isn't there (P:\ not mapped, on a PC with nothing connected), a real
# ADODB.Connection.Open would fail too, for the same underlying reason.
MASTER_DB_PATH = r"P:\ProberMaster.mdb"
LAMP_DB_PATH = r"P:\LampElectricalProbeData.mdb"


def scan_recipes():
    """
    Stand-in for Form_Load's Dir$("C:\\ProbeRecipe\\LampElectrical\\*.PMA") loop
    (frmOpening sub_40b650) that fills comboRecipes.

    Faithful to the original: only the real hardcoded path is scanned, and on a
    PC where it doesn't exist (or is empty), this returns [] - exactly like the
    original's comboRecipes would just stay empty, not populated with anything
    fake.
    """
    if not os.path.isdir(REAL_RECIPE_DIR):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(REAL_RECIPE_DIR)
        if f.lower().endswith(".pma")
    )


def recipe_file_path(name: str) -> str:
    return os.path.join(REAL_RECIPE_DIR, f"{name}.PMA")


def recipe_sibling_paths(name: str) -> list:
    """
    The 6 .PMV/.PMS files WriteMovesFile creates alongside <name>.PMA, named
    "<name>MovesMajorX.PMV" etc - confirmed against the real files present in
    C:\\ProbeRecipe\\LampElectrical on this machine (same convention already
    implemented in gui/electroglas_pma.py's sibling_file_paths(), for the main
    ATA app's Electroglas side - this is the same .PMA/.PMV/.PMS format).
    """
    suffixes = (
        "MovesMajorX.PMV", "MovesMajorY.PMV", "DeviceIDMajor.PMS",
        "MovesMinorX.PMV", "MovesMinorY.PMV", "DeviceIDMinor.PMS",
    )
    return [os.path.join(REAL_RECIPE_DIR, f"{name}{suffix}") for suffix in suffixes]


def missing_recipe_files(name: str) -> list:
    """The .PMA plus any of its 6 siblings that don't actually exist on disk."""
    paths = [recipe_file_path(name)] + recipe_sibling_paths(name)
    return [p for p in paths if not os.path.isfile(p)]


AGT3494A_PROGID = "Agt3494ALib.Agt3494A"


def is_agt3494a_registered() -> bool:
    """
    No longer called anywhere in the running app (2026-07-22) - kept only as a
    documented RE finding. It used to gate opening_form.py's _go_to_runtime()
    with a simulated VB6 run-time error 339, to be faithful to what happens on
    a PC that lacks AGT3494A.OCX. That's no longer the right fidelity target:
    real Agilent documentation confirms AGT3494A.OCX is IntuiLink's generic
    VISA/GPIB ActiveX wrapper, officially discontinued before Windows 7 and
    unsupported on any OS newer than XP - so simulating ITS specific failure
    mode isn't meaningful once Lampexe talks GPIB via pyvisa directly instead
    (see build_hpib_instruments() below), which was never going to depend on
    this OCX at all.

    Original docstring, for reference: stand-in for whether creating an
    Agt3494ALib.Agt3494A ActiveX control would succeed. frmRunTime.frm places
    3 instances of this control (HPIB_Relay1/HPIB_2001X/HPIB_Keithley2400); VB6
    creates all of a form's controls when the form itself is instantiated -
    i.e. right when frmOpening tries to Show frmRunTime - and if the OCX isn't
    registered on this machine, that raises the classic VB6 run-time error 339
    before Form_Load ever runs. Checked via the real Windows registry (stdlib
    winreg): a registered ActiveX control's ProgID resolves to a CLSID under
    HKEY_CLASSES_ROOT.
    """
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{AGT3494A_PROGID}\\CLSID")
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def check_database_connections() -> list:
    """
    Stand-in for Sub Main's two ADODB.Connection.Open calls. Returns a list of
    (title, message) tuples, one per database that "failed to connect" (i.e.
    isn't found on disk) - empty list means both are present. The real handler
    (sub_41eb0b) shows a MsgBox for whichever connection(s) failed and then
    calls __vbaExitProc() - the app never gets as far as showing frmOpening.
    """
    failures = []
    if not os.path.isfile(MASTER_DB_PATH):
        failures.append((
            "IMT LampElectrical Probing",
            "An attempt to make a connection to the Master Prober database failed! "
            "Please alert an engineer.\nWithout this connection the prober cannot run.",
        ))
    if not os.path.isfile(LAMP_DB_PATH):
        failures.append((
            "IMT LampElectrical Probing",
            "An attempt to make a connection to the LampElectrical database failed! "
            "Please alert an engineer.\nWithout this connection the prober cannot run.",
        ))
    return failures


# Stand-in for frmRunTime.Form_Load's tblProberConfiguration lookup
# (binaryninja.txt:11294-12368, fully traced - see Lampexe/GPIB_COMMANDS.txt
# section 0). The real sequence: SELECT * FROM tblProberConfiguration WHERE
# fldProberName = 'LampElectrical' ORDER BY fldInitializeOrder, falling back
# to fldProberName = 'Default' if that's empty; for each row, look up
# Me.Controls("HPIB_" & fldName) and set its .Address to fldAddress. None of
# the 3 instruments' addresses are hardcoded in the real exe - they all come
# from here, including the Keithley's "GPIB0::20" (which also happens to be
# serialized as a stale .frx design-time default, but the DB value is what
# actually gets applied at runtime).
#
# There's no real ProberMaster.mdb reading here (no pyodbc/Jet dependency in
# this project - see this module's own docstring), so this returns a fixed
# mock table shaped like what a real 'LampElectrical' row set would contain,
# instead of an empty list that would leave every instrument unaddressed.
#
# Addresses below are the REAL tblInstruments content (LampElectricalProbeData.mdb),
# read directly via pyodbc from the actual database the user provided (2026-07-22) -
# not a guess, not reverse-engineered. Ground truth query used:
#   SELECT * FROM tblInstruments WHERE fldIsLampElectrical = True
# returns exactly these 3 rows (the other 4 - PS, ExternalDMM, RELAY2, RELAY3 - are
# real instruments on the same GPIB bus but fldIsLampElectrical=False, i.e. not used
# by this app). See Lampexe/GPIB_COMMANDS.txt section 0 for the full writeup,
# including why an earlier version of this file had Keithley2400 wrong (GPIB0::20,
# the .frx's stale unused design-time default, instead of the real GPIB0::24).
_MOCK_PROBER_CONFIG = {
    "LampElectrical": [
        ("2001X", "GPIB0::29::INSTR"),
        ("Relay1", "GPIB0::9::15::INSTR"),
        ("Keithley2400", "GPIB0::24::INSTR"),
    ],
    "Default": [
        ("2001X", "GPIB0::29::INSTR"),
        ("Relay1", "GPIB0::9::15::INSTR"),
        ("Keithley2400", "GPIB0::24::INSTR"),
    ],
}


def load_prober_configuration(prober_name: str = "LampElectrical") -> list:
    """Returns [(fldName, fldAddress), ...] for prober_name, falling back to
    the 'Default' rows if prober_name has none - same fallback the real
    SELECT/re-SELECT does when the first query's recordset is empty."""
    rows = _MOCK_PROBER_CONFIG.get(prober_name)
    if not rows:
        rows = _MOCK_PROBER_CONFIG.get("Default", [])
    return list(rows)


# Real tblProberConfiguration content the user pulled directly from the
# database, 2026-07-22 (fldProberName='IMTPRB02' rows) - see
# Lampexe/GPIB_COMMANDS.txt section 0.7 for the full writeup, including the
# still-open question of exactly how this fldProberName relates to the
# 'LampElectrical'/'Default' query in load_prober_configuration() above (same
# query with a variable prober name, or a different one - not resolved).
# (order, instruction, comment, fld2001XSyntax-or-"") - blank syntax means
# that row is documentation/a flag, not a command to send.
PROBER_INIT_SEQUENCE = [
    (10, "MF/MC on XY MOTION", "on", ""),
    (20, "MF/MC on Z MOTION", "on", ""),
    (30, "MF/MC on Optional Devices", "on", ""),
    (40, "MF/MC on Rest of Commands", "on", "SM15M111100000"),
    (50, "Set Wafer Diameter", "150mm", "SP4D150"),
    (60, "Set Z Scale Factor", "3 steps per mil", "SP12S3"),
    (70, "Set Z Overtravel", "3.7mils", "SP5Z37"),
    (80, "Set Z Clearance", "15 mils", "SP6Z150"),
    (90, "Set Z UpLimit", "420 mils", "SP7Z4200"),
    (100, "Set Z DownLimit", "200 mils", "SP8Z2000"),
    (110, "Set Z Align Height", "216 mils", "SP9Z2160"),
    (120, "Set Z Scan Align Speed", "2000 mils per sec", "SP16V2000"),
    (130, "Set Metric XY Units", "", "SM1U1"),
    (140, "Set Initial Probing Direction", "Quadrant2", "SM2Q2"),
    (150, "Set Probe Mode", "1 = Edge", "SM4P1"),
    (160, "Set Z Travel Mode", "2 = Auto Profile", "SM5E2"),
    (170, "Set Ignore Vacuum", "1 = enabled", "SM22V1"),
    (180, "Set 30mil drop at load", "1 = enabled", "SM30L1"),
    (190, "Set Microprobing", "0 = disabled", "SM35B0"),
    (200, "Set Screen/Lamp Saver", "1= enabled", "SM40S1"),
    (210, "Material Handling", "off", ""),
    (220, "Auto Alignment", "on", ""),
    (230, "Wafer Profiler", "on", ""),
    (240, "Wafer ID reader", "off", ""),
    (250, "SECS protocol", "off", ""),
    (260, "Wafer Mapping", "off", ""),
    (270, "EG TC-2000 Thermal Chuck", "off", ""),
    (280, "Auto Temperature Compensation", "on", "SO01100001"),
    (290, "Temperature Compensation", "0 = disabled", "SX1B0"),
    (300, "Wafer mapping", "0 = disabled", "WM0"),
]


def _load_settings() -> dict:
    if os.path.isfile(_SETTINGS_FILE):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def _save_settings(data: dict) -> None:
    with open(_SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def get_setting(section: str, key: str, default: str) -> str:
    """Stand-in for VB6's GetSetting(appname, section, key, default).

    The original reads/writes HKCU\\Software\\VB and VBA Program
    Settings\\IMTProber\\Names\\ProberName via the registry. This uses a local
    JSON file instead so a demo run never touches the real Windows registry.
    """
    return _load_settings().get(f"{section}/{key}", default)


def save_setting(section: str, key: str, value: str) -> None:
    """Stand-in for VB6's SaveSetting appname, section, key, value."""
    data = _load_settings()
    data[f"{section}/{key}"] = value
    _save_settings(data)


def get_prober_name() -> str:
    return get_setting("Names", "ProberName", DEFAULT_PROBER_NAME)


def set_prober_name(name: str) -> None:
    save_setting("Names", "ProberName", name)


# ---------------------------------------------------------------------------
# Simulated probe run, replacing cmdGo_Click's real sequence on frmRunTime
# (sub_40cba0 - by far the largest handler in the disassembly, ~5000+ lines of
# decompiled HLIL). The real handler: re-validates Wafer ID/Operator/Process
# Step, loads the recipe's .PMA file, sends "SPnXnYn" moves to the Electroglas
# prober over GPIB and checks for an "MC" (move complete) reply, confirms
# align/Z-height with the operator, walks every die sending switch-relay and
# Keithley SCPI commands (the "sens:curr:prot"/"sour:volt"/etc. strings found
# in the disassembly), writes each reading to tblLampElectricalMeasurements,
# and finally sends the stage home.
#
# This stub reproduces the same *shape* of status messages (verbatim strings
# recovered from the disassembly, where they're informational rather than
# real error text) against a handful of fake die IDs, on a timer, so the
# Run Time form's log/behavior looks and feels like the real thing.
# ---------------------------------------------------------------------------

PROBE_DATA_DIR = r"C:\ProbeData"


def uncollected_data_files() -> list:
    """
    C:\\ProbeData\\Complete*.txt files that haven't been collected into the
    database yet (binaryninja.txt ~line 3737-3807: Dir$("C:\\ProbeData\\
    Complete*.txt") feeding "Data files found in C:\\ProbeData that have not
    been collected into the database. You may continue probing, but please
    tell an engineer or the programmer!"). This is a non-blocking warning in
    the original, not a hard stop.
    """
    if not os.path.isdir(PROBE_DATA_DIR):
        return []
    return sorted(f for f in os.listdir(PROBE_DATA_DIR) if f.lower().startswith("complete") and f.lower().endswith(".txt"))


DEMO_DIE_IDS = ["A1", "A2", "A3", "B1", "B2", "B3"]

# comboDies (frmRunTime, Engineering Mode frame) is filled by ~35 AddItem calls in
# Form_Load with no literal string arguments in the disassembly - meaning the item text
# is built at runtime rather than being fixed strings, most likely off the loaded
# recipe's own die list. This is a placeholder list standing in for that until a real
# .PMA reader is wired in (see gui/electroglas_pma.py in the main ATA app for one that
# already exists, if this ever gets integrated there).
DEMO_COMBO_DIES = [f"Die {i:02d}" for i in range(1, 21)]


def build_hpib_instruments() -> dict:
    """
    Real pyvisa-backed replacements for the 3 Agt3494ALib.Agt3494A ActiveX
    instances (HPIB_2001X/HPIB_Relay1/HPIB_Keithley2400), keyed the same way
    load_prober_configuration()'s rows name them ("2001X"/"Relay1"/
    "Keithley2400") so runtime_form.py can look instruments up by fldName.

    Each of these classes already exists in instruments/ (used by gui/app.py,
    the main ATA app, for this exact Electroglas-flavored hardware) and reads
    its own fixed GPIB address out of instruments.yaml at construction time -
    prober_eg/smu_eg/relay1_eg, which are "GPIB0::29::INSTR"/"GPIB0::24::INSTR"
    /"GPIB0::9::15::INSTR" respectively, matching the real DB-sourced addresses
    in _MOCK_PROBER_CONFIG above exactly. GPIBInstrument.__init__ (instruments/
    gpib_base.py) tries to open a real pyvisa session immediately and catches
    the exception if it can't - .inst stays None on failure rather than raising,
    which is what runtime_form.py's "Configure HPIB Failed" check now reads
    instead of the old always-False StubGpibInstrument.is_reachable().

    Relay1 -> HPSwitchbox("relay1_eg") sends standard SCPI CLOS/OPEN (@sccc)
    channel-list commands. Which numeric channel is which die was unresolved
    as of the RE session that built this file - the real exe's own relay
    channel NAMES (RELAY1-RELAY5, FET1-FET4, from its string table, see
    GPIB_COMMANDS.txt section 4) were never confirmed against real E1345A
    hardware. RESOLVED 2026-08-10 (main ATA app, not this RE effort): the
    "probe02" bench in instruments/hp_switchbox.py's BENCH_WIRING was mapped
    directly on this exact machine - closing each channel in turn and
    measuring isolation on a Keithley 2400 - and it's an E1345A mux, the same
    card family GPIB_COMMANDS.txt section 0.6 already identified from the
    disassembly. That IS Relay1 here: two independent traces (this RE effort
    and the on-bench mapping) landing on the same card. real_run_steps()
    below uses BENCH_WIRING["probe02"]["die_sets"] for real per-die routing.
    """
    return {
        "2001X": Electroglas2001X(),
        "Relay1": HPSwitchbox("relay1_eg"),
        "Keithley2400": Keithley2400(),
    }


def simulated_run_steps(die_ids=None):
    """Yields (status_text, is_log_line) steps mimicking the real cmdGo_Click run."""
    die_ids = die_ids or DEMO_DIE_IDS
    yield "Waiting final OK to begin probing", False
    yield "Ready", False
    yield "Moving to first site", True
    for die in die_ids:
        yield f"Probing {die}", True
        yield f"Measuring {die}", True
    yield "Probe Recipe completed normally", True
    yield "Moving to home", True
    yield "Ready", False


# One 2x2 quad shot's die positions, in BENCH_WIRING["probe02"]["die_sets"]'s
# own 1-4 order - the real granularity a LaMP recipe probes per touchdown
# (confirmed 2026-07-22: 4 dies/shot, 2x2 quad). real_run_steps' default,
# unlike DEMO_DIE_IDS above which is arbitrary placeholder labels for the
# text-only simulation and was never meant to line up with real channels.
QUAD_DIE_IDS = ["Die 1", "Die 2", "Die 3", "Die 4"]


def real_run_steps(hpib: dict, die_ids=None):
    """Same (status_text, is_log_line) shape as simulated_run_steps - same
    verbatim recovered strings for fidelity - but for each die this now
    genuinely closes that die's relay channel and takes a real Keithley 2400
    reading, instead of just faking the status text on a timer.

    hpib: build_hpib_instruments()'s return value (or any dict with
    "Relay1"/"Keithley2400" keys). Falls back to text-only exactly like
    simulated_run_steps whenever an instrument's real pyvisa session never
    opened (.inst is None) - same graceful-degradation rule the rest of
    Lampexe already follows (see build_hpib_instruments' docstring), so this
    behaves the same as before on a PC with no GPIB hardware attached.

    Die-to-channel mapping is instruments/hp_switchbox.py's
    BENCH_WIRING["probe02"]["die_sets"] - see build_hpib_instruments'
    docstring for how that got confirmed as this exact rig. Only 4 channels
    are wired (one 2x2 quad); a die_ids list longer than 4 just has no
    channel to close for the extra entries and says so rather than guessing.

    The 10 V / 1 uA-compliance isolation test itself (source voltage, read
    current, report both) matches the real flush-file data this RE effort
    found (fldSetVoltage=fldVoltage=10 fixed, fldCurrent ~1e-9 A range) and
    the same test hp_switchbox.py's module comment describes being used to
    map the channels in the first place.
    """
    die_ids = die_ids or QUAD_DIE_IDS
    relay = hpib.get("Relay1")
    smu = hpib.get("Keithley2400")
    relay_live = relay is not None and relay.inst is not None
    smu_live = smu is not None and smu.inst is not None
    die_sets = bench_wiring("probe02").get("die_sets", {})

    yield "Waiting final OK to begin probing", False
    yield "Ready", False
    yield "Moving to first site", True
    for i, die in enumerate(die_ids, start=1):
        yield f"Probing {die}", True
        chans = die_sets.get(i)
        if relay_live and chans:
            try:
                relay.close_only(chans[0])
                yield f"  CH{chans[0]:02d} closed (die {i} of the quad)", True
            except Exception as e:
                yield f"  relay close failed: {e}", True
        elif not chans:
            yield f"  no relay channel mapped for die {i} - not switched", True
        else:
            yield "  (Relay1 not connected - not switched)", True

        yield f"Measuring {die}", True
        if smu_live:
            try:
                smu.set_voltage("", 10.0)
                smu.set_current_limit("", 1e-6)
                smu.turn_output_on("")
                current = smu.measure_current("")
                smu.turn_output_off("")
                resistance = (10.0 / current) if current else float("inf")
                yield f"  {die}: I={current:.3e} A  R={resistance:.3e} Ohm", True
            except Exception as e:
                yield f"  measurement failed: {e}", True
        else:
            yield "  (Keithley 2400 not connected - not measured)", True

    if relay_live:
        try:
            relay.open_all()
        except Exception:
            pass
    yield "Probe Recipe completed normally", True
    yield "Moving to home", True
    yield "Ready", False
