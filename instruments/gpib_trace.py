"""Command-level tracer for OUR OWN app's instrument traffic - every write/
query/read/serial-poll this process makes, over GPIB or USB (pyvisa treats
both as a MessageBasedResource, so this covers a USB-connected DMM the same
way it covers a GPIB one, no extra code needed), timestamped and handed to
whoever is listening (see add_listener) - the Debug tab's GPIB Trace panel
uses this to show a live log and also write it to a file.

This can only see traffic THIS Python process generates. It cannot see
LabVIEW's own commands - GPIB only allows one active controller session per
address, so a separate pyvisa session generally can't also open an address
LabVIEW already has open, and there is no software-only way to snoop another
process's driver calls. For that, use NI I/O Trace (ships with NI-VISA/488.2 -
Start Menu -> "NI I/O Trace", or NI MAX's Tools menu): it hooks the driver DLL
itself, so it logs every VISA call from ANY process using that driver -
LabVIEW included - with no code changes and no bus contention. Run this
module's trace on our app and NI I/O Trace on LabVIEW, on the same recipe/
measurement, to diff the two command sequences directly.

The patch is installed once (idempotent) and process-global (pyvisa's
MessageBasedResource class, not a per-instance patch) since instrument
objects are constructed all over this codebase, often before any UI exists
to turn tracing on - installing early and gating on `enabled` means Start/
Stop in the GUI is just a flag flip, not a re-patch.
"""

import datetime
import threading

from pyvisa.resources import MessageBasedResource

_lock = threading.Lock()


class _Tracer:
    def __init__(self):
        self.enabled = False
        self._installed = False
        self._log_file = None
        self._listeners = []

    def add_listener(self, fn):
        """fn(line: str) called for every TX/RX/STB event while enabled -
        the GUI panel uses this to append to its live view. Called on
        whatever thread made the instrument call (often a background
        measurement thread), so the listener must hop to the main thread
        itself before touching any Tk widget."""
        self._listeners.append(fn)

    def remove_listener(self, fn):
        try:
            self._listeners.remove(fn)
        except ValueError:
            pass

    def start(self, log_path: str):
        self._install()
        with _lock:
            if self._log_file:
                self._log_file.close()
            self._log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        self.enabled = True
        self._emit("=== trace started ===")

    def stop(self):
        self.enabled = False
        self._emit("=== trace stopped ===")
        with _lock:
            if self._log_file:
                self._log_file.close()
                self._log_file = None

    def _emit(self, line: str):
        ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        entry = f"{ts}  {line}"
        with _lock:
            if self._log_file:
                self._log_file.write(entry + "\n")
        for fn in list(self._listeners):
            try:
                fn(entry)
            except Exception:
                pass

    def _install(self):
        if self._installed:
            return
        self._installed = True

        def addr(resource) -> str:
            return getattr(resource, "resource_name", "?")

        orig_write = MessageBasedResource.write
        orig_read = MessageBasedResource.read
        orig_read_raw = MessageBasedResource.read_raw
        orig_query = MessageBasedResource.query
        orig_read_stb = MessageBasedResource.read_stb

        def traced_write(self_, message, *a, **kw):
            if _tracer.enabled:
                _tracer._emit(f"TX   {addr(self_)}   {message!r}")
            return orig_write(self_, message, *a, **kw)

        def traced_read(self_, *a, **kw):
            resp = orig_read(self_, *a, **kw)
            if _tracer.enabled:
                _tracer._emit(f"RX   {addr(self_)}   {resp!r}")
            return resp

        def traced_read_raw(self_, *a, **kw):
            resp = orig_read_raw(self_, *a, **kw)
            if _tracer.enabled:
                _tracer._emit(f"RX   {addr(self_)}   {resp!r}")
            return resp

        def traced_query(self_, message, *a, **kw):
            if _tracer.enabled:
                _tracer._emit(f"TX   {addr(self_)}   {message!r}")
            resp = orig_query(self_, message, *a, **kw)
            if _tracer.enabled:
                _tracer._emit(f"RX   {addr(self_)}   {resp!r}")
            return resp

        def traced_read_stb(self_, *a, **kw):
            stb = orig_read_stb(self_, *a, **kw)
            if _tracer.enabled:
                _tracer._emit(f"STB  {addr(self_)}   {stb}")
            return stb

        MessageBasedResource.write = traced_write
        MessageBasedResource.read = traced_read
        MessageBasedResource.read_raw = traced_read_raw
        MessageBasedResource.query = traced_query
        MessageBasedResource.read_stb = traced_read_stb


_tracer = _Tracer()

# Module-level convenience wrappers - the GUI panel (and any throwaway
# script) just calls these instead of touching _tracer directly.
start = _tracer.start
stop = _tracer.stop
add_listener = _tracer.add_listener
remove_listener = _tracer.remove_listener


def is_enabled() -> bool:
    return _tracer.enabled
