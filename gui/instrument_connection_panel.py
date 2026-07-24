import threading
import tkinter as tk
from tkinter import messagebox, ttk

from instruments.gpib_base import (
    load_all_instrument_configs, set_instrument_address, ping_address, send_raw_command,
)


def build_address_panel(parent, instruments, log_fn, reconnect_fn, height=220):
    outer = ttk.LabelFrame(parent, text="GPIB / VISA Addresses (instruments.yaml)", padding=6)

    canvas = tk.Canvas(outer, highlightthickness=0, height=height)
    vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    inner = tk.Frame(canvas)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

    def _wheel(e):
        canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")
    canvas.bind("<MouseWheel>", _wheel)
    inner.bind("<MouseWheel>", _wheel)

    try:
        current = load_all_instrument_configs()
    except Exception as e:
        ttk.Label(inner, text=f"Could not read instruments.yaml: {e}",
                  foreground="red").pack(anchor="w")
        current = {}

    addr_vars = {}

    def _ping(name, addr_var, status_var):
        address = addr_var.get().strip()
        if not address:
            status_var.set("no address entered")
            return
        status_var.set("pinging…")
        def _run():
            ok, msg = ping_address(address)
            text = f"{'✅' if ok else '❌'} {msg}"
            inner.after(0, lambda: status_var.set(text))
            log_fn(f"[PING] {name} ({address}): {text}")
        threading.Thread(target=_run, daemon=True).start()

    def _send(name, addr_var, cmd_var, status_var):
        address = addr_var.get().strip()
        cmd = cmd_var.get().strip()
        if not address or not cmd:
            return
        status_var.set("sending…")
        def _run():
            try:
                text = str(send_raw_command(address, cmd))
            except Exception as e:
                text = f"ERROR: {e}"
            inner.after(0, lambda: status_var.set(text))
            log_fn(f"[{name}] >> {cmd!r}  << {text}")
        threading.Thread(target=_run, daemon=True).start()

    for name, key in instruments:
        row_lf = ttk.LabelFrame(inner, text=name, padding=4)
        row_lf.pack(fill="x", padx=2, pady=2)

        addr_row = ttk.Frame(row_lf)
        addr_row.pack(fill="x")
        ttk.Label(addr_row, text="Address:", width=8, anchor="w").pack(side="left")
        address = (current.get(key) or {}).get("address", "")
        addr_var = tk.StringVar(value=address)
        ttk.Entry(addr_row, textvariable=addr_var, width=26, font=("Consolas", 9)).pack(
            side="left", padx=(2, 6))
        ping_status = tk.StringVar(value="—")
        ttk.Button(addr_row, text="Ping", width=6,
                   command=lambda n=name, av=addr_var, sv=ping_status:
                   _ping(n, av, sv)).pack(side="left")
        ttk.Label(addr_row, textvariable=ping_status, foreground="#0077cc",
                  font=("Consolas", 8), wraplength=260, justify="left").pack(
                  side="left", padx=(6, 0))
        addr_vars[key] = addr_var

        cmd_row = ttk.Frame(row_lf)
        cmd_row.pack(fill="x", pady=(2, 0))
        ttk.Label(cmd_row, text="Command:", width=8, anchor="w").pack(side="left")
        cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(cmd_row, textvariable=cmd_var, width=20, font=("Consolas", 9))
        cmd_entry.pack(side="left", padx=(2, 6))
        send_status = tk.StringVar(value="")
        cmd_entry.bind("<Return>", lambda e, n=name, av=addr_var, cv=cmd_var, sv=send_status:
                        _send(n, av, cv, sv))
        ttk.Button(cmd_row, text="Send", width=6,
                   command=lambda n=name, av=addr_var, cv=cmd_var, sv=send_status:
                   _send(n, av, cv, sv)).pack(side="left")
        ttk.Label(cmd_row, textvariable=send_status, foreground="gray",
                  font=("Consolas", 8), wraplength=260, justify="left").pack(
                  side="left", padx=(6, 0))

    ttk.Label(outer, text="Ping/Send act on the address typed above right now, saved or not. "
                          "Commands ending or starting with '?' are sent as queries.",
              foreground="gray", font=("Arial", 8)).pack(anchor="w", pady=(4, 0))

    def _save_all():
        try:
            for name, key in instruments:
                address = addr_vars[key].get().strip()
                if not address:
                    messagebox.showerror("Invalid Address", f"Address for '{name}' cannot be empty.")
                    return
                set_instrument_address(key, address)
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))
            return
        log_fn("[SYSTEM] GPIB addresses saved to instruments.yaml — reconnecting...")
        reconnect_fn()

    ttk.Button(outer, text="Save & Reconnect All", command=_save_all).pack(anchor="e", pady=(6, 0))

    return outer
