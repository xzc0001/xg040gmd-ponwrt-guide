"""Concise, complete stock -> PonWrt -> live-line replacement instructions."""
from usb_commands import USB_FIND, USB_BACKUP

SECTIONS = []
FLOW = []
BOOT = 'bootloader/pbs05-v2026.07-4/'
PRELOADER = BOOT + 'an7581-nokia-xg-040g-md-preloader.bin'
FIP = BOOT + 'an7581-nokia-xg-040g-md-bl31-u-boot.fip'
SYSTEM = 'firmware/PonWrt-MD-20261015/ponwrt-airoha-an7581-nokia_xg-040g-md-ubi-squashfs-sysupgrade.itb'


def section(key, title, blocks, stage='reference'):
    s = dict(id=key, title=title, blocks=blocks, stage=stage)
    SECTIONS.append(s)
    return s


def step(key, title, actions, expected, problem, extra=(), stage='prepare'):
    FLOW.append(key)
    return section(key, f'{len(FLOW):02d}  {title}', [
        ('steps', actions), ('lead', '通过后：' + expected),
        ('p', '不符合时：' + problem), *extra,
    ], stage)


def code(title, text):
    return ('code', dict(title=title, text=text.strip()))


def table(columns, rows):
    return ('table', dict(columns=columns, rows=rows))


section('start', '从这里开始：备份 → 刷入 → 替换现用光猫', [
    ('p', '目标：把新 Nokia XG-040G-MD 刷成 PonWrt，再替换当前 192.168.1.1 的现用光猫。按 01—19 顺序操作，勾选实际完成的步骤。'),
    ('lead', '这版包含完整刷写流程；备份通过后继续，不再停在备份阶段。遇到明确的不支持、读写报错或缺接入参数时，停在对应步骤。'),
    table(['设备/阶段', '电脑接哪里', '打开什么'], [
        ['现用光猫（准确型号看标签）', '原有网络', 'http://192.168.1.1，仅记录现网设置'],
        ['新 XG 原厂系统', '电脑单独直连新 XG LAN2/3', '新 XG 标签地址，常见也是 192.168.1.1'],
        ['pbs05 U-Boot 恢复页', '电脑设 192.168.0.2/24，接新 XG LAN2/3', 'http://192.168.0.1'],
        ['PonWrt 系统', '电脑恢复自动获取，仍接新 XG', '通常 http://192.168.1.1'],
    ]),
    ('p', '两台设备可能都用 192.168.1.1。准备期间让新 XG 与现有家庭 LAN 分开；切换光纤前保留旧光猫原配置。XG 没有 Wi-Fi，家中无线设备还需要独立 AP 或路由器的 AP 模式。'),
    ('p', '软件：PonWrt MD UBI 2026-10-15 社区预发布（a57faf9）、pbs05 MD U-Boot v2026.07-4、Stock2UBI v0.1.14。HTML 自带全文搜索、命令复制和进度导出，断网可用。'),
])

step('old-line', '先抄下现用光猫的接入参数', [
    '暂时保持原网络和光纤不动，打开现用光猫 http://192.168.1.1。记录标签的准确型号，不用“青春版”商品名判断 PON 制式。',
    '在状态/PON/注册信息、WAN/互联网连接页面截图，填写包内 docs/接入参数记录表.txt。能导出配置就再导出一份。',
    '记录实际 PON 模式、认证方式与认证字段、业务 VLAN/优先级、PPPoE 或 DHCP、IPv6；如果由外接路由器拨号，宽带账号密码在那台路由器或运营商处取得。',
], '现网认证、上网方式和所需参数已离线保存，再处理新 XG。',
     '看不到密码、认证方式或线路模式时先记录“未知”；可以先备份新 XG，但不要在缺关键参数时切换主网。', [
    table(['抄自现用光猫/现网路由器', '之后用于 PonWrt'], [
        ['实际工作模式（不能仅写 Auto）', '选择 Line mode'],
        ['SN、LOID/密码、Registration-ID/PLOAM（按现网实际认证）', 'PON 认证；这些名称不能互相混填'],
        ['ONU 厂商/设备/硬件/软件字段（能查看的部分）', 'OLT 确实需要时填写兼容身份'],
        ['互联网 VLAN/优先级、路由/桥接、PPPoE/DHCP、拨号凭据', '建立一体路由的 WAN'],
        ['IPTV/语音配置（需要才记录）', '另行恢复和验收对应业务'],
    ]),
    ('p', '本包驱动：XG-PON、10G-EPON 10G/1G 已测试；XGS-PON、10G-EPON 10G/10G 未测试；GPON、EPON 1G/1G 尚未实现。若现网是尚未实现的模式，本包不能完成这次光猫替换，保留旧光猫。'),
])

step('materials', '准备工具包和 U 盘', [
    '完整解压 XG040GMD-PonWrt-Full-Kit-20261016 到本地短路径，例如 C:\\XG040GMD。双击 03-Verify-Kit.cmd，必须看到 PASS。',
    '准备 FAT32 U 盘，至少 2GB 空闲。把 scripts/collect-device-info.sh、scripts/backup-stock-to-usb.sh 原样复制到 U 盘根目录，再安全弹出。',
    '手机再留一份本 HTML；确认可以搜索、复制命令、导出进度。准备原装电源、网线和保存第二份备份的另一块介质。',
], '文件校验通过、两个 .sh 已在 U 盘根目录。', '不在 ZIP 中运行程序；不格式化有资料的盘；先显示 Windows 的文件扩展名，避免 .sh.txt。')

step('network', '电脑单独连接新 XG', [
    'Win+R 输入 ncpa.cpl，拍照保存当前以太网 IPv4/DNS 设置，再把电脑改为自动获取 IP/DNS。',
    '新 XG 只接原装电源，先不接光纤和 TTL、不按 Reset，等约 2 分钟。',
    '电脑网线从原网络拔下，直接接新 XG LAN2 或 LAN3。不要把两台光猫的 LAN 相连。电脑暂时没有外网属正常。',
], 'Windows 执行 ipconfig，能看到直连以太网的地址；按新 XG 标签打开原厂网页。',
     '169.254.x.x 表示没拿到 DHCP：换 LAN2/3 或网线。标签明确为 192.168.1.1 时才临时设电脑 192.168.1.2、掩码 255.255.255.0、网关/DNS 留空。', [code('在 Windows 终端执行', 'ipconfig')])

step('stock-web', '登录新 XG，记录原厂版本', [
    '用 http:// 打开新 XG 的实际标签地址。确认页面型号为 XG-040G-MD，记录硬件版本和完整原厂软件版本。',
    '优先使用你已取得的超级管理员账号密码。需要默认示例时看下表，注意大小写。',
    '能导出配置就保存；拍下本机 PON/光模块页面。先不改地区、不恢复出厂。',
], '已进入新 XG 的超级管理员页面，型号和原厂版本已保存。',
     '下面是设备 Wiki 所列原厂示例，运营商/卖家可能改过。失败时用你已有超密，不连续猜，不为找回默认密码先 Reset。', [
    table(['用途', '账号', '密码'], [
        ['XG 原厂网页超管示例 [S1]', '以设备/运营商为准', 'YOUR_STOCK_ADMIN_PASSWORD'],
        ['原厂 Telnet 普通登录', '标签上的 user（或本机标签账号）', '机身标签对应的普通用户密码'],
        ['刷好后的 PonWrt', 'root', '镜像默认未设密码；首次留空进入后设置自己的密码'],
    ]),
    ('p', '原厂设备页的账号示例对应新 XG 原厂网页，不能据此登录现用光猫，也不是 PPPoE、LOID 或 PonWrt 密码。'),
])

step('telnet', '开启新 XG Telnet，取得 root', [
    '保持新 XG 超管网页登录，在“应用 > 家庭存储 > FTP”启用 FTP。然后在同一浏览器访问下面的 Telnet 地址；IP 不同就改成新 XG 实际地址。',
    '打开 01-Open-Telnet.cmd，PuTTY 选择 Telnet、端口 23、主机为新 XG。用标签普通账号/密码登录，密码输入不显示字符。',
    '执行 id。不是 uid=0 时，常见 user 批次执行 su user_ftp，输入标签普通密码，再执行 id。',
], '明确看到 uid=0 后继续；网页超管不等于 root。',
     'useradmin 批次可能对应 su useradmin_ftp；只用与本机匹配的路径。unknown user、认证失败或端口不开时先查故障索引，不启动迁移。', [
    code('在浏览器地址栏输入（仅新 XG 为 192.168.1.1 时）', 'http://192.168.1.1/system.cgi?telnet'),
    code('在新 XG 的 PuTTY 窗口执行：先看权限；输入 su 密码后再执行一次', 'id'),
    code('仅当前尚非 root 且匹配 user 批次时执行；回车后输入标签普通密码', 'su user_ftp'),
])

step('inspect', '确认内核、架构和 NAND', [
    '在新 XG root Shell 复制下面命令，保存输出或拍照。',
    '所备免拆程序默认要求 uname -r 为 5.4.55、uname -m 为 aarch64；保存 /proc/mtd 原样表格和 NAND/坏块/ECC 日志。',
], '标准环境可继续准备；不同内核也可先备份，不能强行运行不匹配的迁移模块。',
     'NAND 未识别、不可纠正 ECC 或读取报错时不进入擦写。不同型号/布局不能靠改脚本凑成标准样例。', [
    code('在新 XG root Shell 执行', "id\nuname -r\nuname -m\ncat /proc/mtd\ncat /proc/mounts\ndf -k\ndmesg | grep -iE 'nand|skyhigh|fudan|s35ml|fm25|bad|ecc'"),
])

step('usb-backup', '把新 XG 全部原厂分区备份到 U 盘', [
    '插入放好两个 .sh 的 U 盘，等约 15 秒。先复制“定位 U 盘”，看到 USB_READY 后，再复制“执行备份”。',
    '等待逐个 Reading mtdN 完成，不关终端、不拔盘。成功应出现 Backup stored on USB，保存它显示的完整目录。',
    '备份结束后执行 sync 和 umount；卸载成功再拔盘。',
], 'U 盘得到整套 xg040gmd-stock-... 目录，并含 COMPLETE.txt、分区表、设备端校验单和日志。',
     'STOP、FAILED.txt、dd 读错或没有 USB_READY 都不能当作成功；不要改到 /tmp 或添加 conv=noerror。', [
    code('在新 XG root Shell：定位 U 盘', USB_FIND),
    code('在新 XG root Shell：仅 USB_READY 后执行备份', USB_BACKUP),
    code('在新 XG root Shell：仅备份已经结束后安全卸载', 'sync\numount "$XG_USB_ROOT"'),
    ('p', 'busy 时先关闭访问 U 盘的 FTP/其他窗口再重试，不强制拔盘。脚本只读 MTD，输出到真实 USB/SD 挂载点；所有重叠 MTD 视图都保留，不能拼接成整片镜像。'),
])

step('verify-backup', '电脑校验备份，导出本机 bosa/ri', [
    'U 盘接电脑，把整个 xg040gmd-stock-... 目录复制到 backup/ORIGINAL/，同时保存 device-info-...txt。',
    '双击 08-Verify-Backup.cmd，粘贴刚复制的完整备份目录路径。必须看到所有分区 PASS 和最终 PASS。',
    '通过后在 backup/BOARD-DATA/ 得到本机 bosa.bin、ri.bin 和来源记录。把整套备份、日志、BOARD-DATA 再复制到另一块介质。',
], '两份独立备份已保存，且知道本机 bosa.bin、ri.bin 在哪里；继续第 09 步检查后刷写。',
     '缺文件、大小或哈希错误就重新复制/读取，不改设备校验单；有 NAND/ECC 告警要查清。PASS 只证明大小/传输一致，不证明 NAND 健康或整片恢复可行。', [
    ('p', 'bosa/ri 必须来自这台新 XG 的原厂备份，通常各 262144 字节；编号由脚本按本机分区名确定。现用光猫的配置导出文件、身份或其他机器的 ri 不能拿来替代这两份校准/板级文件。'),
])

step('ready', '刷写前核对这 4 件事', [
    '新设备确实为 XG-040G-MD，已取得 root，内核 5.4.55 / aarch64；NAND 型号已记录，读取/坏块/ECC 问题已查清。',
    '第 08 步已通过，第二份备份已保存，本机 bosa/ri 已导出。',
    '现网 PON 制式、认证和上网参数已明确；普通 GPON/1G EPON 不适用本包，未测试模式不能当作已确认替代方案。',
    '电源稳定、电脑不休眠、网线仍直连新 XG LAN2/3；旧光猫保留原配置，光纤暂时仍留在旧设备。',
], '全部具备后继续第 10 步，开始免拆迁移和真实刷写。',
     '任何一项不具备就先保留原厂状态，查明设备和接入条件后继续。')

step('migration', '复制并运行 Stock2UBI', [
    '电脑把 migration/Stock2UBI-v0.1.14/an758x-stock2ubi 复制到 U 盘根目录，保留原有两个 .sh。U 盘插回新 XG。',
    '重新登录新 XG root Shell；重新执行第 07 步“定位 U 盘”，必须出现 USB_READY。再执行下面复制/校验命令。',
    'SHA256 必须匹配；没有 sha256sum 时使用 md5sum 核对下方 MD5。匹配后执行 chmod 和启动命令，保持 PuTTY 窗口。',
], '浏览器打开 http://新XG原厂IP:3333/，出现“1.备份分区”。',
     '内核不匹配、MTD unlock failed 或 Invalid module format 时停；不加 --ignore-kernel-version。启动程序会尝试解除 MTD 写保护。', [
    code('在新 XG root Shell：复制到 RAM 并核对传输', 'uname -r\nuname -m\ncp "$XG_USB_ROOT/an758x-stock2ubi" /tmp/an758x-stock2ubi\nsha256sum /tmp/an758x-stock2ubi'),
    table(['校验方式', '必须一致的值（不是命令）'], [
        ['SHA256', 'a4e08ab8df5c0f12e314b885ab2280b19cd702fe0d371e8fe5fb20b466334f41'],
        ['MD5（只作本地传输备用校验）', 'f8ec5f1079e06dcea550f9a5c1a17722'],
    ]),
    code('仅原厂没有 sha256sum 时，在新 XG root Shell 执行备用校验', 'md5sum /tmp/an758x-stock2ubi'),
    code('在新 XG root Shell：仅校验一致后运行', 'chmod +x /tmp/an758x-stock2ubi\n/tmp/an758x-stock2ubi'),
])

step('bootloader', '网页刷入配套 MD 引导', [
    '在 Stock2UBI 网页确认备份分区列表，点击“继续”进入“2.刷入恢复引导”。',
    'BL2 栏选择下表 preloader，FIP 栏选择下表 FIP。核对都是 MD、v2026.07-4。',
    '点击“刷入引导 / Install bootloader”，等待回读校验成功并自动重启。不要断电或拔线。',
], '成功后网页/终端失联属预期，等待约 1 分钟，继续第 12 步。',
     '报部分写入失败时保持电源和当前终端，不主动重启；保存错误，查故障索引。', [
    table(['文件栏', '从完整包选择'], [['BL2 / preloader', PRELOADER], ['BL31 + U-Boot FIP', FIP]]),
])

step('uboot', '进入 U-Boot，首次重建 UBI', [
    '电脑 IPv4 改为 192.168.0.2，掩码 255.255.255.0，网关/DNS 留空；仍接新 XG LAN2/3。',
    '浏览器打开 http://192.168.0.1/，确认页面机型为 XG-040G-MD。',
    '打开“刷机 / Flash”，在“UBI 操作”点击“重建 UBI / Rebuild UBI”，等待成功。',
], 'UBI 重建成功，立即继续写 FIP。',
     '恢复页不通先查电脑网段、网口和电源；页面机型不符就不上传。首次重建会清空 UBI；以后普通升级不要再次重建。')

step('fip', '把 FIP 写回 UBI', [
    '在“刷写 U-Boot / Flash U-Boot”FIP 栏，选择下方同一份 MD FIP。',
    '点击“上传并写入 / Upload and write”，等页面明确成功。',
], 'FIP 写入成功，再恢复本机 bosa/ri。',
     '失败就停在恢复页，不点启动、不主动断电。重建后需要再次写 FIP，不能因第 11 步传过而跳过。', [code('电脑文件选择器：FIP 相对完整包的位置', FIP)])

step('board-data', '恢复新 XG 自己的 bosa 和 ri', [
    '在“板级数据 / Board data”中找到 bosa。选第 08 步导出的本机 bosa.bin，上传写入，等待成功。',
    '找到 ri，选同一导出目录的本机 ri.bin，上传写入，等待成功。',
], 'bosa、ri 两项都写入成功，继续安装系统。',
     '文件来源不清、长度异常或写入失败就停。不要把华为的文件、别人的校准或原始 mtd 编号猜成 bosa/ri。')

step('system', '刷入 PonWrt，启动系统', [
    '在“刷写系统 / Install system”的 sysupgrade 栏选择下方普通 MD 永久系统镜像。',
    '点击“上传并刷写 / Upload and flash”，等页面明确成功。',
    '确认 FIP、bosa、ri、系统全部成功，再点击“启动系统 / Boot system”，等数分钟。',
], 'PonWrt 开始启动，继续第 16 步登录。',
     '不选 initramfs-recovery.itb（临时救援）、USB-SFP 改装版或旧 factory.bin。写入报错先保存错误，不反复重建 UBI。', [code('电脑文件选择器：永久系统镜像', SYSTEM)])

step('pon-setup', '登录 PonWrt，填写 PON 参数', [
    '电脑改回自动获取 IP/DNS，拔插网线，用 ipconfig 查看新地址；通常打开 http://192.168.1.1。确认 PonWrt/MD，以 root 登录，镜像初始未设密码时留空，进入后立即设置自己的管理密码。',
    '打开“网络 > PON > 配置”，Line mode 填现网实际模式。按第 01 步记录填写真正用到的 SN/Registration-ID、LOID/密码；按页面分栏填写，不把这些字段互相混填。',
    '保存并应用。需要时通过 PuTTY SSH 22 登录 root，执行下面重启 PON 命令让线路模式/身份生效；此时不再使用原厂 Telnet。',
], '配置已保存，光纤未接时 LOS/未注册属正常，继续切换光纤。',
     '如果运营商按旧光猫 SN 绑定，需要使用你自己线路允许的已登记身份，或让运营商变更绑定；只换光猫不一定自动注册。', [
    table(['字段', '填什么'], [
        ['Line mode', '第 01 步确认的实际线路模式，不能凭华为品牌猜'],
        ['SN', '按本线路绑定要求填写；页面支持 16 位十六进制或 4 个厂商字符 + 8 位十六进制'],
        ['Registration-ID / LOID / LOID password', '分别填现网实际认证字段；未使用的字段不从网上复制值'],
        ['ONU identity：厂商/设备/硬件/软件/Operator', 'OLT 要求时按旧光猫实际记录；原页面没有的字段先保留，不能用商品名编造'],
        ['OMCC version', '默认 0xb0；仅确认 Huawei OLT 兼容问题时按上游提示尝试 0x86。旧光猫是华为不代表局端也是华为'],
    ]),
    code('在 PonWrt 的 SSH 终端执行：配置保存后重启 PON 服务', '/etc/init.d/airoha-pond restart'),
    ('p', '配置层的线路认证身份与本机 bosa/ri 板级数据分开处理。恢复本机校准后，再按你的现网绑定要求配置认证。'),
])

step('fiber', '切换光纤，先确认注册', [
    '准备好把光纤接回华为的退路。给旧光猫断电，从它的 PON 口拔下入户光纤，接到新 XG 的匹配 PON 口；两台设备不同时接入同一条线路。',
    '保护接头，不直视纤头、不强弯；插头或光接口不匹配就停，不硬插。等待并查看 PonWrt 的 PON 状态。',
    '先看光信号，再看 XG-PON 的 O5/OMCI/认证，或 EPON 对应注册状态；执行下面命令可查看详细状态。',
], '光信号正常、注册成功，且协议数据通道已应用后，再设置互联网 WAN。',
     'LOS/功率异常先查光纤和本机校准；O5 但没网先查 OMCI/数据通道，不重刷引导。注册失败且无法解决时按“恢复旧光猫”处理。', [
    code('在 PonWrt SSH 中执行：只读状态', "ponctl --device pon0 status --json\npondctl status --line line0\npondctl datapath --line line0\nlogread | grep -iE 'pon|omci|ploam|en7572|bosa|calib'"),
])

step('wan', '配置一体路由的 WAN', [
    '“网络 > 接口”编辑互联网 WAN：现网 PPPoE 就填自己的宽带账号密码；IPoE/DHCP 就按实际选择。桥接旧光猫的拨号通常原来在外接路由器上。',
    '本机默认光纤 WAN 设备是 pon0。只有确认主机侧需要业务 VLAN 时，才在“网络 > 设备 > 添加设备 > VLAN 802.1q”以 pon0 建立实际 VID，再把 WAN 设备选为 pon0.VID。',
    '若 PON 数据通道已提供去标签的业务，WAN 使用 pon0，不再套一层 VLAN。结合第 01 步原配置与 PON 数据通道状态确认，不能因旧 VLAN 有数值就无条件再加标签。',
    'WAN 归入 wan 防火墙区域，保留正常 WAN 转发/NAT；LAN 提供 DHCP/DNS。保存应用，查看拨号/租约、IP 和 DNS。',
], '电脑能打开网页，WAN 获得预期地址；再接回家庭设备。',
     '不知道 VLAN、认证或去标签位置时不能编一个全国通用值；保存状态输出，先接回旧光猫恢复上网，再查明配置。注册成功并不自动证明互联网/IPTV/语音可用。', [
    ('p', 'PonWrt 可以使用原来的 192.168.1.1，但这时旧光猫已退出家庭 LAN。新系统若有 WAN6，也按原线路方式核对 IPv6；不要只看 IPv4 一次测速。'),
])

step('acceptance', '接回家庭设备，完成验收', [
    '电脑直连测试网页、DNS、IPv4/IPv6和上下行。先确认重启后能重新注册和上网，再做一次断电冷启动测试。',
    '把家庭设备接到新 XG 的 LAN。若继续用原路由器发 Wi-Fi，把它改为 AP 模式，停用旧拨号/第二个 DHCP，并给管理地址避开 PonWrt；按该路由器 AP 模式要求接线。',
    '测试 LAN1—LAN4，以及你需要的 IPTV/语音。XG 本身没有 Wi-Fi，不能省掉无线 AP。',
    '在 PonWrt“系统 > 备份/升级”保存配置备份；连同原厂分区备份、接入记录和本机 bosa/ri 私下留存。',
], 'PonWrt 已刷入，并在你的运营商线路上完成注册、上网、冷启动和所需业务验收，才算替换完成。',
     '任一核心业务不通，先保留日志并恢复旧光猫；不要靠再次重建 UBI 解决业务参数问题。', [
    ('p', '以后升级用匹配 MD UBI/PON 的系统镜像直接刷写系统，不重复重建 UBI、不常规重刷 BL2/FIP。当前构建已含 LAN1 复位修正；千兆电脑测速不能证明 2.5G 上限。'),
])

section('trouble-stock', '排查：原厂与备份', [
    table(['现象', '先做什么', '何时停下'], [
        ['网页打不开 / 打开了华为', '电脑单独直连新 XG LAN2/3，看 ipconfig 和标签地址，使用 http://。', '设备身份或管理地址不明时不 Reset。'],
        ['169.254 地址', '核对自动获取，换网线/网口；标签明确时按第 03 步临时设 IP。', '不把电脑设为光猫相同地址。'],
        ['原厂超管登录失败', '用你已有的本机超管凭据，核对大小写。', '运营商/卖家可能改过；不为恢复默认先清空配置。'],
        ['密码输入没有字符', '这是 Telnet 正常隐藏，输入正确密码后回车。', '连续认证失败先停，避免锁定。'],
        ['su unknown user / uid 非 0', '核对 FTP 开关、标签账号及该固件 su 路径。', '不启动备份或迁移。'],
        ['没有 USB_READY / mounts=2', '两个 .sh 放根目录，换兼容 FAT32/USB2 盘，移除多余盘，看 /proc/mounts。', '不把 XG_USB_ROOT 改成 /tmp。'],
        ['sh 报 \\r / syntax error', '从包内原样重新复制 .sh，避免 BOM/CRLF/.sh.txt。', '不边改脚本边刷写。'],
        ['空间不足 / 只读盘', 'df 检查真实 U 盘容量和读写属性，换有足够空间的盘。', '不删除光猫系统文件。'],
        ['dd 失败 / FAILED.txt', '保留已生成目录、读日志和 dmesg，查电源/盘和 NAND。', '不加 conv=noerror 掩盖读错。'],
        ['Missing / Length / hash mismatch', '复制完整目录重验；仍失败就重新读取，保留设备校验单。', '不修改校验单或 proc-mtd 来通过。'],
    ]),
])

section('trouble-flash', '排查：迁移、启动和 PON', [
    table(['阶段/现象', '处理'], [
        ['Stock2UBI 无法运行 / Exec format error', '程序运行在新 XG 的 root Shell，确认 aarch64、完整传输、chmod +x；不是 Windows EXE。'],
        ['内核不符 / MTD unlock failed', '保存原错误，不忽略版本检查、不加载未知 .ko。'],
        ['3333 不通', 'PuTTY 中程序需仍运行；用新 XG 原厂实际 IP:3333，不用 U-Boot 地址。'],
        ['刷引导报部分写入失败', '保留当前供电/终端和全部错误，不主动重启，先恢复电脑外网求助。'],
        ['U-Boot 恢复页不通', '电脑 192.168.0.2/24，LAN2/3，等约一分钟，打开 http://192.168.0.1。'],
        ['FIP / bosa / ri / 系统写入失败', '停在恢复页，核对文件、来源、长度和包校验；缺 FIP 时不启动，不反复重建。'],
        ['Boot system 后 .0.1 不通', '系统地址变了：电脑改 DHCP，查地址，通常访问 http://192.168.1.1。'],
        ['系统起不来但 U-Boot 仍在', '安装后上电约一秒再按住 Reset 进入该引导 Web 恢复，先查 FIP/板级数据/系统；不要套用原厂 Reset 时序。'],
        ['LOS / 光功率 / 校准异常', '查匹配光纤、接头、本机 bosa/ri；不要借其他机器校准。'],
        ['光信号正常，注册失败', '核对现网制式、实际 SN/认证、OMCI/OAM/OLT 兼容；不凭旧光猫厂商推断 OLT。'],
        ['O5/已注册，仍不能上网', '查 pondctl datapath、OMCI 映射、VLAN、PPPoE/DHCP、DNS/防火墙；不能靠刷引导解决。'],
        ['LOID conflict / 认证冲突', '检查旧设备确已退出该线路和身份/绑定要求；不拿第二个 ONU 同时试。'],
        ['只有 LAN1 异常', '先用 LAN2/3 管理，核对本包 a57faf9 和冷启动结果，保存日志。'],
    ]),
    ('p', 'U-Boot 高级页的 RAM boot 可用匹配 recovery.itb 临时救援。“整片恢复”要求实际覆盖范围、坏块/OOB和偏移都匹配；不能把 mtdN 文件拼接，也不能因文件叫 all_flash 就无条件上传整片恢复。'),
])

section('serial', '备用：CH340 串口与传文件', [
    ('steps', ['免拆主线不接 TTL。需要看启动日志时插 CH340/CH341，运行 05-Check-Serial.cmd；无 COM 再安装 drivers/CH340-CH341/CH341SER.EXE。', '确认 TX/RX 是 3.3V TTL。光猫断电后按 PCB 丝印接 GND—GND、适配器 TX—板 RX、适配器 RX—板 TX；VCC 不接，仍用原装电源。', '04-Open-TeraTerm.cmd 选实际 COM，115200、8N1、无流控，先记录启动日志。无输出先查共地和 TX/RX，不接 VCC 试错。']),
    ('p', '只有实际日志明确等待 XMODEM 才发送该阶段文件。BL2 请求 FIP 时用本包 MD bl31-u-boot.fip；BootROM 和 BL2 不是同一阶段，不套一个通用发送顺序。'),
    ('p', '优先用 U 盘。02-Open-WinSCP.cmd 连接原厂时按已启用的 FTP 账号设置，FTP 21 端口；06-HTTP-Transfer.cmd 是依赖本机 Python 的备用传输；07-Open-Tftpd64.cmd 移动目录后需重选 tftp-root 和直连网卡。'),
])

section('rollback', '替换没成功：接回旧光猫恢复上网', [
    ('steps', ['若还停在新 XG 原厂备份阶段，直接把电脑网线接回原网络即可；无须重置任何光猫。', '若 PonWrt 无法替代，给新 XG 断电，把入户光纤接回原华为，给华为通电，恢复原来的家庭接线。', '如果改过旧路由器 AP/拨号设置，按之前保存的记录恢复；先不改华为的原始认证。', '电脑 ncpa.cpl 恢复原 IPv4/DNS 设置，原来 DHCP 就自动获取；测试原网恢复。']),
    ('p', '这是恢复现网的接线方法，不是把新 XG 整片刷回原厂。若新 XG 正在写入或刚报告部分写入错误，先保持它的供电/恢复会话、保存日志，只将电脑恢复到可联网环境求助。'),
])

section('sources', '版本与依据', [
    ('p', '当前日期 2026-10-16（Asia/Shanghai）。固件固定为 2026-10-15 PonWrt MD UBI 社区预发布，源码 a57faf93c6c3638ba3651690228aabaa51d3f235。它不是 pbs05 官方稳定二进制发布；实际运营商 OLT、认证和业务仍以实机验收为准。'),
    ('bullets', [
        '[S1] 原厂网页账号与 Telnet 访问示例：https://openwrt.org/toh/nokia/xg-040g-md 。本手册不采用该页的其他固件写入或 Reset 指令。',
        '[S2] PonWrt 支持机型：https://github.com/pbs05/ponwrt/blob/master/README_zh.md',
        '[S3] Stock2UBI v0.1.14：https://github.com/pbs05/an758x-stock2ubi/tree/v0.1.14',
        '[S4] pbs05 U-Boot 首次安装顺序：https://github.com/pbs05/uboot-an758x/tree/v2026.07-4',
        '[S5] 本构建 PON 驱动支持表：https://github.com/pbs05/openwrt-pon-drivers/blob/e5194d2dfd169eef8f4a944fdc3f929e0287b680/README.md',
        '[S6] PON 配置、状态命令及 LuCI 源码：https://github.com/pbs05/openwrt-pon-userspace/tree/cce9d756742487b378749c606b30e13ee9b0f093',
        '[S7] 社区成品来源：https://github.com/yonggedebaqi/ponwrt/releases/tag/pangzi',
    ]),
    table(['文件', 'SHA256'], [
        ['MD 永久系统 sysupgrade.itb', '40d3762b71248b418bf00eccc5d2042626af94995fa7a4ad26b1c4147ec4c95e'],
        ['MD 临时救援 recovery.itb', '96b0ab7b4ce57dc97b833316f5510b0c6ec86eeead3a9d2f999f4d4d62b693d7'],
        ['MD preloader.bin', '918909a7009fdaaaa4dc28b5d88082dfd9c282b44a1714a7ac9d6c7cef78462b'],
        ['MD FIP', 'fa1a58332eab5d1ff3910392931f78f741c6c2dafaa4d4978402d6d8bde446e9'],
    ]),
    ('p', '包内 docs/upstream 保留上游说明、profiles/哈希和来源证据。进度文件不包含真实账号密码；认证、原厂备份和日志私下保存。'),
])
