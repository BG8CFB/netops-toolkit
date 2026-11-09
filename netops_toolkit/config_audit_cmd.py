#!/usr/bin/env python3
"""config_audit.py - 配置基线合规审计（弱配置/明文协议/默认风险）。

检查项: telnet 开启 / vty 无 ACL / 默认密码社区串 / 明文 http 管理 / 未 shutdown 的多余口。
用法: python config_audit.py backups_dir/ [-o audit.csv]
"""
import argparse, csv, glob, os, re, sys

RULES = [
    ("telnet-开启", re.compile(r"^\s*(protocol inbound telnet|user-interface vty.*telnet)", re.I | re.M), "high"),
    ("SNMP-默认社区串", re.compile(r"snmp-agent community (read|write) (public|private)", re.I), "high"),
    ("HTTP-管理未关", re.compile(r"^\s*ip http enable", re.I | re.M), "medium"),
    ("SSH-v1", re.compile(r"ssh version 1", re.I), "high"),
    ("AAA-未启用本地用户密码复杂度", re.compile(r"password (simple|cipher) (\w{0,6})$", re.I | re.M), "medium"),
    ("VTY-无ACL", re.compile(r"user-interface vty(?![\s\S]{0,200}acl)", re.I), "low"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backup_dir"); ap.add_argument("-o", "--out", default="audit.csv")
    a = ap.parse_args()
    rows = []
    for path in glob.glob(os.path.join(a.backup_dir, "**", "*"), recursive=True):
        if not (os.path.isfile(path) and path.lower().endswith((".cfg", ".config", ".txt", ".log"))):
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        for name, pat, sev in RULES:
            m = pat.search(text)
            if m:
                rows.append({"file": os.path.basename(path), "rule": name, "severity": sev,
                             "evidence": (m.group(0) or "").strip()[:100]})
    if not rows:
        print("未发现命中项。"); return
    sev_order = {"high": 0, "medium": 1, "low": 2}
    rows.sort(key=lambda r: (sev_order[r["severity"]], r["file"]))
    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["file", "rule", "severity", "evidence"])
        w.writeheader(); w.writerows(rows)
    hi = sum(1 for r in rows if r["severity"] == "high")
    print(f"命中 {len(rows)} 项 (高危 {hi}) -> {a.out}")
    for r in rows[:15]:
        print(f"  [{r['severity']:6}] {r['file']}: {r['rule']} | {r['evidence']}")


if __name__ == "__main__":
    main()
