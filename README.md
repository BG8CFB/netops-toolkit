# netops-toolkit

> 网络工程师自动化小工具集 — H3C / 华为 / 思科 / 锐捷
> network automation toolkit / 批量采集 / 配置审计 / 网络运维脚本

```bash
pip install netops-toolkit
```

## 三个免费命令

```bash
# 1. 批量采集设备信息(版本/CPU/内存/接口) -> CSV
netops-toolkit info devices.yml -o info.csv

# 2. 在配置备份目录搜索 IP/MAC 出现位置
netops-toolkit find backups/ 192.168.10.23

# 3. 离线配置合规审计(telnet/弱社区串/http管理) -> CSV
netops-toolkit audit backups/ -o audit.csv
```

设备清单 devices.yml:

```yaml
devices:
  - name: core-sw1
    host: 192.168.1.1
    vendor: h3c        # h3c/huawei/cisco/ruijie
    username: admin
```

## Pro 版（¥59, 12 个脚本）

批量配置下发(模板+diff确认) / 全网端口定位 / 接口周报 / VLAN 分布图 / STP 根桥审计 / 批量重启 / syslog 批量配置 / DHCP Snooping 核查 …
购买: 2945362558@qq.com（微信/支付宝）

## 相关项目

- [netcfg-vault](https://github.com/BG8CFB/netcfg-vault) — 配置备份 + AES-256-GCM 加密库
- [netops-cheatsheets](https://github.com/BG8CFB/netops-cheatsheets) — 三厂商速查表
- [netops-scripts](https://github.com/BG8CFB/netops-scripts) — Pro 脚本包仓库

MIT License


## v0.2.0 — locate: 全网定位 MAC/IP

```bash
netops-toolkit locate devices.yml aa:bb:cc:dd:ee:ff
netops-toolkit locate devices.yml 10.1.1.23
```

核心/汇聚查 ARP+MAC 表锁定源端口 → 沿 MAC 表逐跳下钻到接入端口, 打印完整定位链。H3C/华为/思科/锐捷四厂商命令适配。
