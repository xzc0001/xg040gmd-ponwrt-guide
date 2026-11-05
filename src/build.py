from html import escape
import json
from pathlib import Path
import re

from guide_content import SECTIONS, FLOW
from html_components import CSS, UI, flattened

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT
OUT = KIT / 'docs'
OUT.mkdir(parents=True, exist_ok=True)


def text_html(text):
    value = escape(text)
    return re.sub(r'https://[^\s。]+', lambda m: '<a href="'+m.group(0)+'" target="_blank" rel="noopener">'+m.group(0)+'</a>', value)


def blocks_html(blocks):
    result = []
    for kind, value in blocks:
        if kind in ('p', 'lead'):
            result.append('<p class="'+kind+'">'+text_html(value)+'</p>')
        elif kind == 'h':
            result.append('<h3>'+escape(value)+'</h3>')
        elif kind in ('steps', 'bullets'):
            tag = 'ol' if kind == 'steps' else 'ul'
            result.append('<'+tag+'>'+''.join('<li>'+text_html(x)+'</li>' for x in value)+'</'+tag+'>')
        elif kind == 'code':
            result.append('<div class="command"><p class="command-title">'+escape(value['title'])+'</p><button type="button" class="copy">复制</button><pre><code>'+escape(value['text'])+'</code></pre></div>')
        elif kind == 'table':
            result.append('<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+escape(x)+'</th>' for x in value['columns'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+text_html(x)+'</td>' for x in row)+'</tr>' for row in value['rows'])+'</tbody></table></div>')
    return '\n'.join(result)


CORE = r'''
const Guide=(()=>{
 const ids=GUIDE_DATA.sections.map(s=>s.id),chapterIds=GUIDE_DATA.chapters;
 const enums={pon:['unknown','xgpon','xgspon','epon10_1','epon10_10','gpon','epon1'],root:['unknown','yes','no'],kernel:['unknown','5.4.55','other'],arch:['unknown','aarch64','other'],backup:['unknown','pass','fail'],params:['unknown','ready','missing']};
 function empty(){return {version:2,current:'start',all:false,done:[],conditions:{pon:'unknown',root:'unknown',kernel:'unknown',arch:'unknown',backup:'unknown',params:'unknown'}}}
 function clean(input){const s=empty();if(!input||typeof input!=='object'||Array.isArray(input))return s;if(ids.includes(input.current))s.current=input.current;s.all=input.all===true;if(Array.isArray(input.done))s.done=[...new Set(input.done.filter(id=>chapterIds.includes(id)))];if(input.conditions&&typeof input.conditions==='object')Object.keys(enums).forEach(k=>{if(enums[k].includes(input.conditions[k]))s.conditions[k]=input.conditions[k]});return s}
 function advice(c){const a=[];
  if(['gpon','epon1'].includes(c.pon))a.push({hold:true,text:'当前驱动尚未实现这个模式。本包不能完成现网光猫替换，保留旧光猫；仍可先备份新 XG。'});
  else if(['xgspon','epon10_10'].includes(c.pon))a.push({hold:true,text:'该模式仍为未测试，不能当作已经确认可替代主网的方案。先保留旧光猫，完成备份并查清兼容性。'});
  else if(c.pon==='unknown')a.push({hold:true,text:'先在现用光猫查实际工作模式。品牌、商品名、Auto 或能力列表不能证明线路制式；未知时先备份，不进入擦写。'});
  else a.push({hold:false,text:'这个模式在本构建中已测试；仍需你自己的校准、认证和 OLT/业务验收。'});
  if(c.root!=='yes')a.push({hold:true,text:c.root==='no'?'uid 不是 0：停在第 05 步，不执行备份或迁移。':'第 05 步执行 id，确认 uid=0 后再执行原厂备份。'});
  if(c.kernel==='other'||c.arch==='other')a.push({hold:true,text:'不满足所备 Stock2UBI 的默认环境。可先只读备份；不忽略内核检查，不加载未知模块。'});
  else if(c.kernel==='unknown'||c.arch==='unknown')a.push({hold:true,text:'第 06 步确认 5.4.55 / aarch64。没有结果时不进入迁移。'});
  if(c.backup==='fail')a.push({hold:true,text:'备份校验失败：按第 08 步和故障索引处理，不进入刷写，不修改设备校验单。'});
  else if(c.backup==='pass')a.push({hold:false,text:'备份长度/传输校验通过后保留另一块介质上的完整副本。PASS 不证明 NAND 健康或整片恢复可行。'});
  else a.push({hold:true,text:'先完成第 07—08 步的全部分区备份、离机校验、本机 bosa/ri 导出和第二份副本。'});
  if(c.params!=='ready')a.push({hold:true,text:'现网接入参数尚未齐全：先保存华为/现网路由器的认证、VLAN、PPPoE 或 DHCP 设置。'});
  if(c.pon==='xgpon'||c.pon==='epon10_1'){
   if(c.root==='yes'&&c.kernel==='5.4.55'&&c.arch==='aarch64'&&c.backup==='pass'&&c.params==='ready')a.push({hold:false,text:'已记录主要条件具备。第 09 步再核对 NAND、第二份备份和电源，然后按第 10—19 步刷写、注册和验收。'});
  }
  return a;
 }
 function next(id){if(id==='start')return chapterIds[0];const i=chapterIds.indexOf(id);return i>=0&&i<chapterIds.length-1?chapterIds[i+1]:null}
 function fault(index){if(index===''||index===null||index===undefined)return null;const n=Number(index);return Number.isInteger(n)&&n>=0&&n<GUIDE_DATA.faults.length?GUIDE_DATA.faults[n]:null}
 function search(query){const terms=String(query).trim().toLowerCase().split(/\s+/).filter(Boolean);if(!terms.length)return [];return GUIDE_DATA.sections.filter(s=>terms.every(t=>(s.title+' '+s.text).toLowerCase().includes(t))).map(s=>{const at=s.text.toLowerCase().indexOf(terms[0]),from=Math.max(0,at-35);return {id:s.id,title:s.title,excerpt:(from?'…':'')+s.text.slice(from,from+140)+'…'}})}
 return {empty,clean,advice,next,fault,search,ids,chapterIds};
})();
'''


def replace_exact(text, old, new, count=1):
    assert text.count(old) == count, (old, text.count(old))
    return text.replace(old, new)


ui = UI
ui = replace_exact(ui, 'legacy-guide-storage-key', 'xg040gmd-ponwrt-full-guide-20261016-v2')
ui = replace_exact(ui, "$('#next').disabled=i===Guide.ids.length-1", "$('#next').disabled=Guide.next(state.current)===null")
ui = replace_exact(ui, "$('#next').textContent=state.current==='verify-backup'?'查看本次完成后的处理':'下一章'", "$('#next').textContent=state.current==='acceptance'?'流程结束':'下一步'")
ui = replace_exact(ui, "state.done.length+' / 9'", "state.done.length+' / '+Guide.chapterIds.length")
ui = replace_exact(ui, "if(state.current==='verify-backup')toast('本次到第 9 章结束。请保存副本并恢复电脑原有网络。');", '')
ui = replace_exact(ui, "setHash('terms')", "setHash('old-line')")
ui = replace_exact(ui, "state.done.length===9", "state.done.length===Guide.chapterIds.length")
ui = replace_exact(ui, '9 章已勾选。请确认第二份备份已保存，然后恢复电脑原有网络。', '全部步骤已勾选。以实际 PON、上网、冷启动和所需业务验收结果为准。')
ui = replace_exact(ui, 'XG040GMD-20261016', 'XG040GMD-PonWrt-Full-20261016', count=2)
ui = replace_exact(ui, 'data.version!==1', 'data.version!==2')
ui = replace_exact(ui, 'XG040GMD-操作进度-', 'XG040GMD-PonWrt-全流程进度-')

data = dict(chapters=FLOW, sections=[dict(id=s['id'], title=s['title'], text=flattened(s['blocks'])) for s in SECTIONS], faults=[])
fault_options = ['<option value="">选择当前现象</option>']
for section_id, group in [('trouble-stock','原厂和备份'),('trouble-flash','刷写、启动和 PON')]:
    fault_options.append('<optgroup label="'+group+'">')
    for kind, val in next(s for s in SECTIONS if s['id']==section_id)['blocks']:
        if kind != 'table':
            continue
        for row in val['rows']:
            fault_options.append('<option value="'+str(len(data['faults']))+'">'+escape(row[0])+'</option>')
            data['faults'].append(dict(section=section_id, title=row[0], lines=row[1:]))
    fault_options.append('</optgroup>')


def nav_link(s):
    tick='<span class="tick" aria-hidden="true">·</span>' if s['id'] in FLOW else ''
    return '<a href="#'+s['id']+'" data-section="'+s['id']+'">'+tick+'<span>'+escape(s['title'])+'</span></a>'


navigation = nav_link(SECTIONS[0])
for title, keys in [('先记录和备份',FLOW[:8]),('迁移和刷入 PonWrt',FLOW[8:15]),('注册和替换现网',FLOW[15:])]:
    navigation += '<p class="nav-title">'+title+'</p><div class="nav-main">'+''.join(nav_link(next(s for s in SECTIONS if s['id']==key)) for key in keys)+'</div>'
navigation += '<details><summary>故障、串口、恢复现网、来源</summary>'+''.join(nav_link(s) for s in SECTIONS if s['id'] not in FLOW and s['id']!='start')+'</details>'
content = []
for s in SECTIONS:
    key=s['id']
    badge=''
    if key in ('bootloader','uboot','fip','board-data','system'):
        badge='<p class="future-note">本步包含实际闪存写入 · 保持供电和当前会话</p>'
    completion=''
    if key in FLOW:
        i=FLOW.index(key)
        completion='<div class="chapter-complete"><label><input type="checkbox" data-check="'+key+'">本步已操作并达到“通过后”的结果</label><p>以设备实际结果为准；遇到异常先按提示处理。</p></div>'
        previous='start' if i==0 else FLOW[i-1]
        following='<a class="button primary" href="#'+FLOW[i+1]+'" data-section="'+FLOW[i+1]+'">下一步 →</a>' if i<len(FLOW)-1 else '<span class="small">流程结束：保存配置与验收记录</span>'
        completion += '<div class="step-controls js-only"><a class="button" href="#'+previous+'" data-section="'+previous+'">← 上一步</a>'+following+'</div>'
    content.append('<section id="'+key+'">'+badge+'<h2>'+escape(s['title'])+'</h2>'+blocks_html(s['blocks'])+completion+'</section>')

conditions='''<div class="condition-grid">
<label>现用光猫的实际 PON 模式<select data-condition="pon"><option value="unknown">未知 / Auto / 仅能力列表</option><option value="xgpon">XG-PON</option><option value="epon10_1">10G-EPON 10G/1G</option><option value="xgspon">XGS-PON</option><option value="epon10_10">10G-EPON 10G/10G</option><option value="gpon">普通 GPON</option><option value="epon1">EPON 1G/1G</option></select></label>
<label>新 XG 的 id 结果<select data-condition="root"><option value="unknown">未检查</option><option value="yes">明确 uid=0</option><option value="no">非 0 / 未登录</option></select></label>
<label>新 XG 原厂 uname -r<select data-condition="kernel"><option value="unknown">未检查</option><option value="5.4.55">5.4.55</option><option value="other">其他</option></select></label>
<label>新 XG 原厂 uname -m<select data-condition="arch"><option value="unknown">未检查</option><option value="aarch64">aarch64</option><option value="other">其他</option></select></label>
<label>全部原厂分区校验<select data-condition="backup"><option value="unknown">未验证</option><option value="pass">长度和设备校验单全部通过</option><option value="fail">有失败/缺文件</option></select></label>
<label>现网认证、VLAN 和上网设置<select data-condition="params"><option value="unknown">尚未整理</option><option value="ready">所需字段已离线保存</option><option value="missing">关键字段仍缺失</option></select></label>
</div>'''
data_json=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
css=CSS+'''
.reading-bar{position:sticky;top:8px;z-index:2}.step-controls{margin-top:19px;gap:10px;justify-content:space-between;align-items:center}.js .step-controls{display:flex}.step-controls .primary{background:var(--blue);color:white}.lead{color:#22533e;background:#f1f7f3;padding:10px 13px;border-radius:5px;font-weight:500}main p{font-size:15px}.future-note{font-weight:500}.nav-title{font-size:13px;font-weight:700}main h2{font-size:24px}@media print{.step-controls{display:none!important}.reading-bar{position:static}}
'''
html='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>XG-040G-MD → PonWrt 全流程交互手册</title><style>'''+css+'''</style></head><body id="top">
<header><p class="eyebrow">离线可用 · 2026-10-16 · 全流程版 v2</p><h1>XG-040G-MD → PonWrt</h1><p class="sub">记录华为现网 → 备份新 XG → 刷引导和系统 → 恢复 PON/WAN → 替换验收<br>每步看操作、通过结果、异常处理。默认按 01—19 顺序继续。</p><div class="header-actions"><button id="start-guide" class="primary js-only" type="button">从第 01 步开始</button><button id="view-all" class="js-only" type="button">展开全文</button><button id="print-guide" class="js-only" type="button">打印正文</button></div></header>
<noscript><p class="nojs notice">JavaScript 未启用，下面仍可读取完整步骤；交互导航、搜索和进度功能需启用 JavaScript。</p></noscript>
<div class="layout"><aside class="sidebar"><div class="progress-box js-only"><p class="progress-label">全流程进度</p><div class="progress-line"><strong id="completed-count">0 / 19</strong><span>步已勾选</span></div><progress id="progress" max="19" value="0" aria-label="已完成步骤"></progress><p id="storage-note" class="storage"></p><div class="save-tools"><button id="export-progress" type="button">导出进度</button><button id="import-progress" type="button">恢复进度</button><input id="progress-file" type="file" accept="application/json,.json" hidden></div></div><nav aria-label="步骤目录">'''+navigation+'''</nav></aside><div class="main-column">
<div class="toolbox js-only"><h2>找步骤 / 查问题</h2><form id="search-form" class="search-row"><input id="search" type="search" placeholder="搜索：超管、USB_READY、VLAN、hash mismatch…" aria-label="搜索全文" autocomplete="off"><button type="submit">搜索</button></form><p id="search-count" class="search-count" aria-live="polite">搜索包含全部步骤和未展开的故障索引。</p><ul id="search-results" class="search-results"></ul><details><summary>按实际结果判断当前条件</summary><p class="small">填写非密码结果；凭据另存在包内接入参数记录表。</p>'''+conditions+'''<div id="advice" class="advice" aria-live="polite"></div></details><details><summary>遇到问题：选现象看处理</summary><label class="fault-label">当前现象<select id="fault">'''+''.join(fault_options)+'''</select></label><div id="fault-output" class="fault-output" aria-live="polite"></div></details></div>
<div id="reading-bar" class="reading-bar"><div class="reading-label"><span id="reading-mode"></span><strong id="current-title"></strong></div><div class="reading-controls"><button id="previous" type="button">上一步</button><button id="next" type="button">下一步</button></div></div><main>'''+''.join(content)+'''</main><footer>本 HTML 可独立离线阅读。实际操作需完整工具包；命令复制只复制文本，需在指定设备/终端执行。<br>流程以刷入 PonWrt 并完成本地线路验收为终点；未在你的实际设备上执行刷写或测试运营商兼容。</footer></div></div><div id="toast" class="toast" role="status" hidden></div><script>
const GUIDE_DATA='''+data_json+';\n'+CORE+ui+'''</script></body></html>'''
(OUT/'index.html').write_text(html,encoding='utf-8')
plain=['XG-040G-MD -> PonWrt 全流程 2026-10-16','按 01—19 操作；备份后继续刷写、注册和验收。','']
for s in SECTIONS:
    plain.extend(['='*60,s['title'],''])
    for kind,val in s['blocks']:
        if kind in ('p','lead','h'):plain.extend([val,''])
        elif kind in ('steps','bullets'):plain.extend([f'{i+1}. {x}' if kind=='steps' else '- '+x for i,x in enumerate(val)]+[''])
        elif kind=='code':plain.extend([val['title'],val['text'],''])
        elif kind=='table':plain.extend([' | '.join(val['columns'])]+[' | '.join(row) for row in val['rows']]+[''])
(OUT/'manual.txt').write_text('\n'.join(plain),encoding='utf-8')
print(json.dumps(dict(kit=str(KIT),steps=len(FLOW),sections=len(SECTIONS),faults=len(data['faults']),html_bytes=(OUT/'index.html').stat().st_size),ensure_ascii=False))
