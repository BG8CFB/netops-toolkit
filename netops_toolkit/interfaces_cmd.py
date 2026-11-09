"""Parse display interface output into a CSV report with error/speed stats."""
from __future__ import annotations

import argparse
import getpass
import os
import sys

CMD = {"h3c": "display interface", "huawei": "display interface",
       "cisco": "show interfaces", "ruijie": "show interfaces"}


def parse_interfaces(text):
    """解析接口名/速率/CRC/错包（尽力而为）。"""
    out = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"^(?:\S+/)?(GigabitEthernet\S+|GE\S+|Eth\S+|Eth-Trunk\d+|Ten\S+|Fa\S+)", line.strip())
        if m:
            if cur: out.append(cur)
            cur = {"iface": m.group(1), "in_bps": "", "out_bps": "", "crc": 0, "errors": 0}
            continue
        if cur is None: continue
        s = line.strip()
        mb = re.search(r"(\d+)\s*bps", s)
        if mb:
            key = "in_bps" if re.search(r"input|Inbound|Last 300 sec", s) else "out_bps"
            if not cur[key]: cur[key] = mb.group(1)
        mc = re.search(r"(\d+)\s*CRC", s, re.I)
        if mc: cur["crc"] = int(mc.group(1))
        me = re.search(r"(\d+)\s*(?:input error|output error|error)", s, re.I)
        if me: cur["errors"] = max(cur["errors"], int(me.group(1)))
    if cur: out.append(cur)
    return out



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inventory"); ap.add_argument("-o", "--out", default="interface_weekly.csv")
    ap.add_argument("-w", "--workers", type=int, default=8)
    a = ap.parse_args()
    password = os.environ.get("NETCFG_PASSWORD") or getpass.getpass("SSH password: ")
    devs = (lambda d: d.get("devices", d) if isinstance(d, dict) else d)(yaml.safe_load(open(a.inventory, encoding="utf-8")))
    rows = []
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {}
        for d in devs:
            def task(d=d):
                c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                c.connect(d["host"], username=d["username"], password=password, timeout=15,
                          look_for_keys=False, allow_agent=False)
                try:
                    _, o, _ = c.exec_command(CMD[d.get("vendor", "h3c")], timeout=60)
                    return o.read().decode("utf-8", "replace")
                finally: c.close()
            futs[ex.submit(task)] = d
        for fut in as_completed(futs):
            d = futs[fut]
            try:
                for it in parse_interfaces(fut.result()):
                    it["device"] = d["name"]; rows.append(it)
            except Exception as e:
                print(f"[FAIL] {d['name']}: {e}")
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["device", "iface", "in_bps", "out_bps", "crc", "errors"])
        w.writeheader(); w.writerows(rows)
    dirty = [r for r in rows if r["crc"] or r["errors"]]
    print(f"{len(rows)} 接口 -> {a.out}; 异常接口 {len(dirty)} 个")
    for r in sorted(dirty, key=lambda x: -(x["crc"] + x["errors"]))[:10]:
        print(f"  {r['device']} {r['iface']}: CRC={r['crc']} errors={r['errors']}")


if __name__ == "__main__":
    main()

