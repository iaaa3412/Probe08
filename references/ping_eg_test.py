"""Exercise the real gui/instruments code path against the live bench.

Run from the project root:
    python references/ping_eg_test.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui"))

from instruments.gpib_base import (  # noqa: E402
    load_all_instrument_configs, discover_bus, ping_address,
)
from instruments_eg_panel import _EG_INSTRUMENTS  # noqa: E402

print("=== Scan Bus: what is actually on this prober ===")
started = time.perf_counter()
for item in discover_bus():
    print(f"  {item['address']:<22} {item['identity'] or '(answers no ID query)'}")
    for line in item["detail"]:
        print(f"  {'':<22}   {line}")
print(f"  scan took {time.perf_counter() - started:.2f} s")

cfg = load_all_instrument_configs()

print("\n=== Ping All (skips instruments not fitted to this prober) ===")
total = 0.0
for name, key, id_queries, fitted, write_probe in _EG_INSTRUMENTS:
    address = cfg[key]["address"]
    if not fitted:
        print(f"  SKIP  {name:<32} {address:<22}      -  not fitted")
        continue
    started = time.perf_counter()
    ok, msg = ping_address(address, id_queries=id_queries, write_probe=write_probe)
    elapsed = time.perf_counter() - started
    total += elapsed
    print(f"  {'OK  ' if ok else 'FAIL'}  {name:<32} {address:<22} "
          f"{elapsed * 1000:6.0f} ms  {msg}")
print(f"\n  pings took {total:.2f} s")
