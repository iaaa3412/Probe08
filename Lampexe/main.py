import sys
import tkinter as tk
from tkinter import messagebox

import data_stub
from opening_form import OpeningForm

# The real prjLampElectrical.exe's Project.vbp sets Startup="Sub Main" rather than a
# form - the actual first thing that runs (basGlobalProbing's sub_41e8a0, see
# disassembledlamp-reverse-engineering memory notes) opens ADODB connections to
# P:\ProberMaster.mdb and P:\LampElectricalProbeData.mdb, and if either fails it
# shows a fatal MsgBox and exits via __vbaExitProc() - frmOpening never appears at
# all. That gate is reproduced here (data_stub.check_database_connections(), a
# file-existence proxy for "would the connection succeed" - see its docstring) so
# a PC with neither database mapped behaves the same way the real exe would: it
# refuses to start, instead of silently letting you proceed into a fake run.

if __name__ == "__main__":
    failures = data_stub.check_database_connections()
    if failures:
        root = tk.Tk()
        root.withdraw()
        for title, message in failures:
            messagebox.showerror(title, message)
        root.destroy()
        sys.exit(1)

    app = OpeningForm()
    app.mainloop()
