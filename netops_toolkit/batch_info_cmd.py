#!/usr/bin/env python3
"""batch_info.py - 批量采集网络设备信息，输出 CSV。

用法: python batch_info.py devices.yml [-o out.csv]
密码: 环境变量 NETCFG_PASSWORD 或运行时提示输入。
支持: h3c / huawei / cisco / ruijie (SSH)
"""
import argparse, csv, getpass, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import paramiko
    import yaml
except ImportError:
    sys.exit("缺少依赖: pip install paramiko pyyaml")

INFO_COMMANDS = {
    "h3c":     ["display version", "display cpu-usage", "display memory", "display interface brief"],
    "huawei":  ["display version", "display cpu-usage", "display memory-usage", "display interface brief"],
    "cisco":   ["show version", "show processes cpu sorted | exclude 0.00", "show memory statistics", "show ip interface brief"],
    "ruijie":  ["show version", "show cpu", "show memory", "show interface status"],
}


def load_devices(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    devs = data.get("devices", data) if isinstance(data, dict) else data
    for d in devs:
        for k in ("name", "host", "vendor", "username"):
            if k not in d:
                raise SystemExit(f"设备清单缺少字段 {k}: {d}")
    return devs


def run_commands(dev, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(dev["host"], username=dev["username"], password=password,
                   timeout=15, look_for_keys=False, allow_agent=False)
    out = {}
    try:
        for cmd in INFO_COMMANDS[dev["vendor"]]:
            _, stdout, _ = client.exec_command(cmd, timeout=30)
            out[cmd] = stdout.read().decode("utf-8", "replace")
    finally:
        client.close()
    return out


def extract(dev, raw):
    """从原始回显提取关键字段（尽力而为，缺省留空）。"""
    all_text = "\n".join(raw.values())
    def find(pat):
        import re
        m = re.search(pat, all_text)
        return m.group(1) if m else ""
    return {
        "name": dev["name"], "host": dev["host"], "vendor": dev["vendor"],
        "version": find(r"(?:Version|version)\s+(?:V|v)?([\w.]+)"),
        "cpu": find(r"(\d+(?:\.\d+)?)\s*%?\s*(?:in past|cpu)", ),
        "mem": find(r"(\d+)%.*memory") or find(r"memory.*?(\d+)%"),
        "uptime": find(r"(?:uptime is|up)\s+(.+?)(?:\n|$)"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inventory")
    ap.add_argument("-o", "--out", default="device_info.csv")
    ap.add_argument("-w", "--workers", type=int, default=8)
    args = ap.parse_args()
    password = os.environ.get("NETCFG_PASSWORD") or getpass.getpass("SSH password: ")
    devs = load_devices(args.inventory)
    rows, errs = [], []
    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(run_commands, d, password): d for d in devs}
        for fut in as_completed(futs):
            d = futs[fut]
            try:
                rows.append(extract(d, fut.result()))
                print(f"[OK] {d['name']}")
            except Exception as e:
                errs.append((d["name"], str(e)))
                print(f"[FAIL] {d['name']}: {e}")
    with open(args.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["name", "host", "vendor", "version", "cpu", "mem", "uptime"])
        w.writeheader(); w.writerows(rows)
    print(f"\n{len(rows)} 台成功, {len(errs)} 台失败 -> {args.out}")


if __name__ == "__main__":
    main()
