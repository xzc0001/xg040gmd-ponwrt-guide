# XG-040G-MD PonWrt 刷机交互手册

面向新手的离线手册：记录现网 → 备份全部原厂分区 → 校验 → Stock2UBI 免拆迁移 → pbs05 U-Boot → PonWrt → PON/WAN → 替换验收。

每步给出操作、预期结果和异常处理；提供 19 步导航、命令复制、进度导出/恢复、搜索和故障索引。

## 阅读

下载仓库 ZIP 并解压，双击 `Open-Guide.cmd`，或用浏览器打开 [docs/index.html](docs/index.html)。不需要服务器、npm 或联网。文件移动或换浏览器前先导出进度。

仓库是**手册及备份辅助脚本项目**，不包含可直接刷入的固件、Windows 软件、驱动、原厂备份或私密配置。手册中的 `00-Open-Manual.cmd`、`03-Verify-Kit.cmd`、`08-Verify-Backup.cmd` 和目录路径沿用配套离线工具包约定，不是本仓库已内置的可执行工具包。

已有配套工具包：将 `docs/index.html` 更新到该包 `manual/index.html` 使用；不要把 HTML 更新误当作固件升级。尚未准备工具包：先按 [下载清单](docs/downloads.json) 的来源、版本、SHA256 和手册路径准备文件。系统镜像在所列社区归档内，需要解压取普通 MD UBI sysupgrade/recovery，不能使用 MF/TF、USB-SFP 或同名其他构建。

## 适用范围

- 对象是 Nokia **XG-040G-MD UBI**；不等于 MF/TF。
- 免拆路线需要原厂 root、匹配的 AArch64/内核及 NAND 条件。不能强行忽略版本检查。
- 文档使用 **2026-10-15 固定历史组合**：PonWrt 社区预发布 a57faf9、pbs05 U-Boot v2026.07-4、Stock2UBI v0.1.14；不是最新版本推荐。
- 此锁定驱动中 XG-PON、10G-EPON 10G/1G 已测试；XGS-PON、10G-EPON 10G/10G 未测试；GPON、EPON 1G/1G 尚未实现。不能推导更新版本的支持情况。
- 刷写会修改闪存；先备份并校验全部原厂分区和本机 bosa/ri。文档不保证每台 NAND、本地 OLT、认证及全部业务兼容。

## 脱敏与配置

[配置结构示例](docs/example-settings.md) 保留非身份配置结构；[空白记录模板](docs/connection-record.example.txt) 只能填入自己的本地副本。不要提交真实 SN/LOID、宽带凭据、WAN 地址、IPv6 前缀、MAC、设备序列号、原厂转储或日志。

备份辅助脚本只读取设备 MTD 并写到真实 U 盘；电脑校验器不访问设备。脚本不能替代 NAND 健康评估或保证整片恢复。

## 构建和校验

```sh
python src/build.py
python tests/check_project.py
node tests/navigation.cjs
```

Python 3 和 Node.js 仅用于构建/检查；阅读 HTML 不需要安装。生成文件不带个人进度；进度由浏览器本地保存，导出文件不要提交。测试覆盖导航/条件逻辑与文本一致性，未声称实际光猫或每个浏览器交互已验收。

## 上游与许可

- [PonWrt](https://github.com/pbs05/ponwrt)
- [Stock2UBI](https://github.com/pbs05/an758x-stock2ubi)
- [pbs05 U-Boot](https://github.com/pbs05/uboot-an758x)
- [PON 驱动](https://github.com/pbs05/openwrt-pon-drivers)
- [PON 用户态](https://github.com/pbs05/openwrt-pon-userspace)
- [原厂访问参考](https://openwrt.org/toh/nokia/xg-040g-md)

本仓库原创手册、页面代码和辅助脚本采用 MIT，见 [LICENSE](LICENSE)。上游项目、工具和固件各自遵循其原始许可，本仓库不重新授权这些产物。
