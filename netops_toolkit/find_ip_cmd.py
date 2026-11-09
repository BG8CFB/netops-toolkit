#!/usr/bin/env python3
"""find_ip.py - 在设备配置备份目录中搜索 IP/MAC/关键字出现位置。

用法: python find_ip.py backups_dir 192.168.10.23
      python find_ip.py backups_dir vlan 100   (第二个参数为文件内 glob)
适合: 定位某 IP 配置在哪些设备/接口，配合 netcfg-vault 备份目录使用。
"""
import argparse, glob, os, re, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("backup_dir", help="配置备份根目录（递归搜索 *.cfg *.config *.txt）")
    ap.add_argument("pattern", help="IP / MAC / 关键字")
    args = ap.parse_args()
    pat = re.compile(re.escape(args.pattern), re.IGNORECASE)
    hits = 0
    for path in glob.glob(os.path.join(args.backup_dir, "**", "*"), recursive=True):
        if not (os.path.isfile(path) and path.lower().endswith((".cfg", ".config", ".txt", ".log"))):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        lines = [l for l in text.splitlines() if pat.search(l)]
        if lines:
            hits += 1
            print(f"\n=== {path} ===")
            for l in lines[:20]:
                print("  " + l.strip()[:120])
            if len(lines) > 20:
                print(f"  ... 共 {len(lines)} 行")
    if not hits:
        print(f"未找到 '{args.pattern}'")
    else:
        print(f"\n共 {hits} 个文件命中")


if __name__ == "__main__":
    main()
