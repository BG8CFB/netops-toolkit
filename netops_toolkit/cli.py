#!/usr/bin/env python3
"""netops-toolkit CLI 入口: 把各子命令串起来。"""
import argparse, sys


def main(argv=None):
    ap = argparse.ArgumentParser(prog="netops-toolkit", description="网络工程师自动化小工具集")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("info", help="批量采集设备信息 -> CSV")
    p1.add_argument("inventory"); p1.add_argument("-o", "--out", default="device_info.csv")
    p1.add_argument("-w", "--workers", type=int, default=8)
    p2 = sub.add_parser("find", help="在配置备份目录搜索 IP/MAC/关键字")
    p2.add_argument("backup_dir"); p2.add_argument("pattern")
    p3 = sub.add_parser("audit", help="离线配置合规审计 -> CSV")
    p3.add_argument("backup_dir"); p3.add_argument("-o", "--out", default="audit.csv")
    a = ap.parse_args(argv)
    if a.cmd == "info":
        from .batch_info_cmd import main as m
        sys.argv = ["batch_info", a.inventory, "-o", a.out, "-w", str(a.workers)]
        m()
    elif a.cmd == "find":
        from .find_ip_cmd import main as m
        sys.argv = ["find_ip", a.backup_dir, a.pattern]
        m()
    elif a.cmd == "audit":
        from .config_audit_cmd import main as m
        sys.argv = ["config_audit", a.backup_dir, "-o", a.out]
        m()


if __name__ == "__main__":
    main()
