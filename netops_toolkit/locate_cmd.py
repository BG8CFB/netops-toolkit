"""Locate a MAC or IP address across every device in the inventory.

Walks MAC/ARP tables hop by hop and prints the access port chain.
"""
from __future__ import annotations

import argparse
import getpass
import os
import re
import sys

try:
    import paramiko
    import yaml
except ImportError:
    sys.exit("缺少依赖: pip install paramiko pyyaml")

SHOW = {
    "h3c":    {"mac": "display mac-address {mac}", "arp": "display arp all | include {ip}"},
    "huawei": {"mac": "display mac-address {mac}", "arp": "display arp all | include {ip}"},
    "cisco":  {"mac": "show mac address-table address {mac}", "arp": "show ip arp {ip}"},
    "ruijie": {"mac": "show mac-address-table address {mac}", "arp": "show arp | include {ip}"},
}


def run(dev, password, cmd):
    c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(dev["host"], username=dev["username"], password=password, timeout=15,
              look_for_keys=False, allow_agent=False)
    try:
        _, o, _ = c.exec_command(cmd, timeout=30)
        return o.read().decode("utf-8", "replace")
    finally:
        c.close()



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inventory"); ap.add_argument("target", help="MAC 或 IP")
    a = ap.parse_args()
    password = os.environ.get("NETCFG_PASSWORD") or getpass.getpass("SSH password: ")
    devs = (lambda d: d.get("devices", d) if isinstance(d, dict) else d)(yaml.safe_load(open(a.inventory, encoding="utf-8")))
    tgt = a.target.lower()
    is_ip = re.match(r"^\d+\.\d+\.\d+\.\d+$", tgt)
    print(f"目标: {tgt} ({'IP' if is_ip else 'MAC'})\n")
    found = []
    for d in devs:
        cmds = SHOW[d.get("vendor", "h3c")]
        try:
            if is_ip:
                out = run(d, password, cmds["arp"].replace("{ip}", tgt))
            else:
                out = run(d, password, cmds["mac"].replace("{mac}", tgt))
            # 提取含端口的行
            for line in out.splitlines():
                if (not is_ip and tgt in line.lower()) or (is_ip and tgt in line):
                    port = re.search(r"(GE\S*\d+/\d+/\d+|GigabitEthernet\S*\d+/\d+/\d+|Eth\S*\d+/\d+|Eth-Trunk\d+|BAG\d+|Fa\S*\d+/\d+|Te\S*\d+/\d+)", line)
                    if port:
                        found.append((d["name"], port.group(1), line.strip()[:110]))
        except Exception as e:
            print(f"[skip] {d['name']}: {e}")
    if not found:
        print("未在 MAC/ARP 表中找到目标。"); return
    for name, port, line in found:
        print(f"[{name}] {port}\n    {line}")
    print(f"\n提示: 取「最下层」设备（非上联口）的端口即为接入位置。")


if __name__ == "__main__":
    main()

