#!/usr/bin/env python3
"""topology: 从配置备份中提取 LLDP/CDP 邻居, 生成全网邻接表 (CSV + Mermaid 图).

输入: 备份目录 (含各设备配置/显示输出文件).
输出: edges CSV (local_device, local_port, neighbor, neighbor_port) 与可选 Mermaid 图.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# LLDP: lldp neighbor Brief (H3C/华为) 行样例: GE1/0/1  sw-core  GE1/0/24
_LLDP_ROW = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")
# CDP: Device ID Local Intrfce Holdtme Capability Platform Port ID
_CDP_ROW = re.compile(r"^(\S+)\s+(\S+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$")

CFG_EXT = {".cfg", ".config", ".txt", ".log"}


def _neighbors_from_text(name: str, text: str):
    edges = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        toks = s.split()
        if len(toks) == 4 and "/" in toks[0] and "/" in toks[3]:
            if toks[2].lower() != "total":
                edges.append((name, toks[0], toks[2], toks[3], "lldp"))
                continue
        if len(toks) == 3 and "/" in toks[0] and "/" in toks[2]:
            if toks[1].lower() != "total":
                edges.append((name, toks[0], toks[1], toks[2], "lldp"))
                continue
        if len(toks) >= 5 and "/" in toks[1] and "/" in toks[-1] and toks[0].lower() not in ("device", "device-id", "deviceid") and not toks[0].startswith("-") and not toks[1].lower().startswith("local"):
            # CDP: 设备名 本地接口 ... 对端端口 (能力列可能多 token, 用首尾锚定)
            edges.append((name, toks[1], toks[0], toks[-1], "cdp"))
            continue
    return edges


def build_topology(cfg_dir: str):
    root = Path(cfg_dir)
    all_edges = []
    for p in sorted(root.iterdir()):
        if p.suffix.lower() not in CFG_EXT or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        all_edges.extend(_neighbors_from_text(p.stem, text))
    return all_edges


def write_csv(edges, out: str) -> None:
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["local_device", "local_port", "neighbor", "neighbor_port", "protocol"])
        w.writerows(edges)


def write_mermaid(edges, out: str) -> None:
    seen = set()
    rows = []
    for ld, lp, nd, np_, proto in edges:
        key = (ld, nd)
        if key in seen:
            continue
        seen.add(key)
        rows.append("  %s --- %s" % (ld, nd))
    body = "graph LR\n" + "\n".join(rows) + "\n"
    Path(out).write_text(body, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(prog="topology", description="从备份提取 LLDP/CDP 邻居 -> 邻接表")
    ap.add_argument("backup_dir")
    ap.add_argument("-o", "--out", default="topology_edges.csv")
    ap.add_argument("--mermaid", default=None, help="可选: 输出 Mermaid 图 .md")
    a = ap.parse_args()
    edges = build_topology(a.backup_dir)
    if not edges:
        print("no LLDP/CDP neighbors found in", a.backup_dir)
        raise SystemExit(1)
    write_csv(edges, a.out)
    if a.mermaid:
        write_mermaid(edges, a.mermaid)
    print("devices edges: %d -> %s" % (len(edges), a.out))


if __name__ == "__main__":
    main()
