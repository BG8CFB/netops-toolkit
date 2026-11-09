"""Batch save device running-configs to a timestamped archive directory."""
from __future__ import annotations

import argparse
import getpass
import os
import sys

SAVE = {"h3c": "save force", "huawei": "save", "cisco": "write memory", "ruijie": "write"}
SHOW = {"h3c": "display current-configuration", "huawei": "display current-configuration",
        "cisco": "show running-config", "ruijie": "show running-config"}



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inventory"); ap.add_argument("-o", "--out", default="archive")
    ap.add_argument("-w", "--workers", type=int, default=8)
    a = ap.parse_args()
    password = os.environ.get("NETCFG_PASSWORD") or getpass.getpass("SSH password: ")
    devs = (lambda d: d.get("devices", d) if isinstance(d, dict) else d)(yaml.safe_load(open(a.inventory, encoding="utf-8")))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(a.out, stamp); os.makedirs(outdir, exist_ok=True)
    def task(d):
        c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(d["host"], username=d["username"], password=password, timeout=15,
                  look_for_keys=False, allow_agent=False)
        try:
            _, o, _ = c.exec_command(SAVE[d.get("vendor", "h3c")], timeout=60)
            o.channel.recv_exit_status()
            _, o2, _ = c.exec_command(SHOW[d.get("vendor", "h3c")], timeout=60)
            cfg = o2.read().decode("utf-8", "replace")
        finally: c.close()
        p = os.path.join(outdir, d["name"] + ".cfg")
        open(p, "w", encoding="utf-8").write(cfg)
        return p
    ok = fail = 0
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(task, d): d for d in devs}
        for fut in as_completed(futs):
            d = futs[fut]
            try: print(f"[OK] {d['name']} -> {fut.result()}"); ok += 1
            except Exception as e: print(f"[FAIL] {d['name']}: {e}"); fail += 1
    print(f"\n{ok}/{ok+fail} 台, 归档目录 {outdir}")


if __name__ == "__main__":
    main()

