# netops-toolkit

> 网络工程师自动化小工具集 — H3C / 华为 / 思科 / 锐捷
> 交换机批量采集 / MAC定位 / 接口报表 / 配置审计 / 拓扑提取 全部免费

```bash
pip install netops-toolkit
```

## 七个免费命令 (v0.4.0)

```bash
# 1. 批量采集设备信息(版本/CPU/内存/接口) -> CSV
netops-toolkit info devices.yml -o info.csv

# 2. 在配置备份目录搜索 IP/MAC 出现位置
netops-toolkit find backups/ 192.168.10.23

# 3. 离线配置合规审计(telnet/弱社区串/http管理) -> CSV
netops-toolkit audit backups/ -o audit.csv

# 4. 批量保存配置并归档
netops-toolkit save devices.yml -o archive/

# 5. 接口流量/CRC/错包报表
netops-toolkit interfaces devices.yml -o interfaces.csv

# 6. 全网 MAC/IP 定位到接入端口(核心->汇聚->接入逐跳下钻)
netops-toolkit locate devices.yml aa-bb-cc-dd-ee-ff

# 7. 从 LLDP/CDP 备份输出提取拓扑 -> CSV + Mermaid 图
netops-toolkit topology backups/ -o edges.csv --mermaid topo.mmd
```

设备清单 devices.yml:

```yaml
devices:
  - name: core-sw1
    host: 192.168.1.1
    vendor: h3c        # h3c/huawei/cisco/ruijie
    username: admin
```

## Pro 脚本包（¥59, 6 个高危运维脚本）

批量配置下发(模板+diff确认) / 批量重启 / syslog 批量配置 / VLAN 分布图 / STP 根桥审计 / DHCP Snooping 核查
购买: 2945362558@qq.com（微信/支付宝）· [脚本清单](https://github.com/BG8CFB/netops-scripts)

## 相关项目

- [netcfg-vault](https://github.com/BG8CFB/netcfg-vault) — 配置备份 + AES-256-GCM 加密库 + 定时任务 + 巡检报告
- [netops-cheatsheets](https://github.com/BG8CFB/netops-cheatsheets) — 三厂商速查表 / [命令对照表](https://bg8cfb.github.io/netops-cheatsheets/command-map.html)
- [netops-scripts](https://github.com/BG8CFB/netops-scripts) — Pro 脚本包仓库

MIT License
