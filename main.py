"""Launch the Atomica Tester GUI.

Entry point: `python main.py` from the repository root. The application itself
lives in gui/app.py, which stays runnable directly (`python gui/app.py`) - this
only spares anyone the guess about which file starts it.
"""
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
# gui/ modules import each other by bare name ("import app_settings"), so both
# the package root and gui/ have to be importable.
for path in (ROOT, os.path.join(ROOT, "gui")):
    if path not in sys.path:
        sys.path.insert(0, path)

if __name__ == "__main__":
    # run_path with __main__ so app.py's single-instance guard and mainloop
    # fire exactly as they do when it is launched directly.
    runpy.run_path(os.path.join(ROOT, "gui", "app.py"), run_name="__main__")
